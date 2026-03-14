"""
GroupManager 插件测试

测试插件的核心功能。
"""

import sys
from unittest.mock import MagicMock

# Mock astrbot（测试环境未安装）
_astrbot_mock = MagicMock()
for mod in ['astrbot', 'astrbot.api', 'astrbot.api.event',
            'astrbot.api.star', 'astrbot.api.message_components']:
    sys.modules.setdefault(mod, _astrbot_mock)

import pytest
from gm_core.core.validator import Validator, RuleType, ValidationResult
from gm_core.core.config import Config


class MockContext:
    """模拟 AstrBot Context 用于测试"""

    def __init__(self, config_dict: dict = None):
        self._config = config_dict or {}

    def get_config(self):
        return self._config


class TestValidator:
    """验证器测试类"""

    def test_is_regex_pattern(self):
        """测试正则表达式模式识别"""
        validator = Validator()

        assert validator.is_regex_pattern("/\\d{11}/") is True
        assert validator.is_regex_pattern("/[a-z]+/") is True

        assert validator.is_regex_pattern("学生") is False
        assert validator.is_regex_pattern("123456") is False

    def test_validate_regex(self):
        """测试正则表达式验证"""
        validator = Validator()

        is_valid, error = validator.validate_regex("\\d{11}")
        assert is_valid is True
        assert error is None

        is_valid, error = validator.validate_regex("[invalid")
        assert is_valid is False
        assert error is not None

    def test_test_pattern(self):
        """测试模式匹配"""
        validator = Validator()

        is_valid, is_matched, error = validator.test_pattern("/\\d{11}/", "13812345678")
        assert is_valid is True
        assert is_matched is True
        assert error is None

        is_valid, is_matched, error = validator.test_pattern("/\\d{11}/", "abc")
        assert is_valid is True
        assert is_matched is False
        assert error is None

        is_valid, is_matched, error = validator.test_pattern("学生", "我是学生")
        assert is_valid is True
        assert is_matched is True
        assert error is None

        is_valid, is_matched, error = validator.test_pattern("学生", "我是老师")
        assert is_valid is True
        assert is_matched is False
        assert error is None


class TestConfig:
    """配置测试类"""

    def test_default_mode(self):
        """测试默认模式"""
        config = Config(MockContext({"default_mode": "reject"}))
        assert config.default_mode == "reject"

        config = Config(MockContext({}))
        assert config.default_mode == "allow"

    def test_enable_logging(self):
        """测试启用日志"""
        config = Config(MockContext({"enable_logging": False}))
        assert config.enable_logging is False

        config = Config(MockContext({}))
        assert config.enable_logging is True

    def test_auto_sync(self):
        """测试配置自动同步"""
        ctx = MockContext({"default_mode": "allow"})
        config = Config(ctx)
        assert config.default_mode == "allow"

        # 模拟配置变更
        ctx._config["default_mode"] = "reject"
        # 不需要重新初始化，自动同步
        assert config.default_mode == "reject"


class TestStoragePerGroupIsolation:
    """测试每群独立配置的完整隔离性"""

    @pytest.fixture
    def storage(self):
        """创建带 mock KV 存储的 Storage 实例"""
        from gm_core.core.storage import Storage

        kv_store = {}

        plugin = MagicMock()

        async def mock_get(key, default=None):
            return kv_store.get(key, default)

        async def mock_put(key, value):
            kv_store[key] = value

        plugin.get_kv_data = mock_get
        plugin.put_kv_data = mock_put

        s = Storage(plugin)
        s._kv_store = kv_store  # 暴露出来方便断言
        return s

    @pytest.mark.asyncio
    async def test_group_enable_isolation(self, storage):
        """群A启用不影响群B"""
        await storage.enable_group("group_A")

        assert await storage.is_group_enabled("group_A") is True
        assert await storage.is_group_enabled("group_B") is False

    @pytest.mark.asyncio
    async def test_group_admin_isolation(self, storage):
        """群A的管理员不出现在群B"""
        await storage.add_group_admin("group_A", "admin_1")
        await storage.add_group_admin("group_B", "admin_2")

        a_admins = await storage.get_group_admins("group_A")
        b_admins = await storage.get_group_admins("group_B")

        assert a_admins == ["admin_1"]
        assert b_admins == ["admin_2"]
        assert "admin_1" not in b_admins
        assert "admin_2" not in a_admins

    @pytest.mark.asyncio
    async def test_group_rules_isolation(self, storage):
        """群A的规则不出现在群B"""
        await storage.save_group_rules("group_A", [
            {"pattern": "学生", "type": "keyword"}
        ])
        await storage.save_group_rules("group_B", [
            {"pattern": "/\\d{4}/", "type": "regex"}
        ])

        a_rules = await storage.get_group_rules("group_A")
        b_rules = await storage.get_group_rules("group_B")

        assert len(a_rules) == 1
        assert a_rules[0]["pattern"] == "学生"
        assert len(b_rules) == 1
        assert b_rules[0]["pattern"] == "/\\d{4}/"

    @pytest.mark.asyncio
    async def test_whitelist_blacklist_isolation(self, storage):
        """群A的白名单/黑名单不影响群B"""
        await storage.add_to_whitelist("group_A", "user_good")
        await storage.add_to_blacklist("group_A", "user_bad")

        # 群B 应该为空
        assert await storage.get_group_whitelist("group_B") == []
        assert await storage.get_group_blacklist("group_B") == []

        # 群A 有数据
        assert "user_good" in await storage.get_group_whitelist("group_A")
        assert "user_bad" in await storage.get_group_blacklist("group_A")

    @pytest.mark.asyncio
    async def test_group_setting_override(self, storage):
        """群独立 default_mode 覆盖全局配置"""
        # 群A 设置 reject，群B 没设置
        await storage.set_group_setting("group_A", "default_mode", "reject")

        a_mode = await storage.get_group_setting("group_A", "default_mode", None)
        b_mode = await storage.get_group_setting("group_B", "default_mode", None)

        assert a_mode == "reject"
        assert b_mode is None  # 群B 无独立配置，应回退到全局

    @pytest.mark.asyncio
    async def test_kv_keys_are_per_group(self, storage):
        """验证 KV 存储 key 确实包含 group_id"""
        await storage.enable_group("111")
        await storage.save_group_rules("222", [{"p": "test"}])
        await storage.add_to_whitelist("333", "u1")
        await storage.add_to_blacklist("444", "u2")

        keys = set(storage._kv_store.keys())
        assert "group_config_111" in keys
        assert "rules_222" in keys
        assert "whitelist_333" in keys
        assert "blacklist_444" in keys

        # 不存在交叉 key
        assert "rules_111" not in keys
        assert "whitelist_111" not in keys

    @pytest.mark.asyncio
    async def test_full_scenario_two_groups(self, storage):
        """完整场景：两个群各自独立操作互不干扰"""
        # 群A: 启用、加规则、加白名单、加管理员
        await storage.enable_group("group_A")
        await storage.save_group_rules("group_A", [
            {"pattern": "你好", "type": "keyword"}
        ])
        await storage.add_to_whitelist("group_A", "vip_user")
        await storage.add_group_admin("group_A", "boss_A")

        # 群B: 启用、加不同规则、加黑名单、加不同管理员
        await storage.enable_group("group_B")
        await storage.save_group_rules("group_B", [
            {"pattern": "/\\d{6}/", "type": "regex"}
        ])
        await storage.add_to_blacklist("group_B", "spammer")
        await storage.add_group_admin("group_B", "boss_B")

        # 验证完全隔离
        assert await storage.get_group_rules("group_A") == [{"pattern": "你好", "type": "keyword"}]
        assert await storage.get_group_rules("group_B") == [{"pattern": "/\\d{6}/", "type": "regex"}]

        assert await storage.get_group_whitelist("group_A") == ["vip_user"]
        assert await storage.get_group_whitelist("group_B") == []

        assert await storage.get_group_blacklist("group_A") == []
        assert await storage.get_group_blacklist("group_B") == ["spammer"]

        assert await storage.get_group_admins("group_A") == ["boss_A"]
        assert await storage.get_group_admins("group_B") == ["boss_B"]

        # 禁用群A不影响群B
        await storage.disable_group("group_A")
        assert await storage.is_group_enabled("group_A") is False
        assert await storage.is_group_enabled("group_B") is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
