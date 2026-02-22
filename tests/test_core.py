"""
GroupManager 插件测试

测试插件的核心功能。
"""

import pytest
from groupmanager.core import Config, Validator, RuleType, ValidationResult


class TestValidator:
    """验证器测试类"""

    def test_is_regex_pattern(self):
        """测试正则表达式模式识别"""
        validator = Validator()

        # 测试正则表达式
        assert validator.is_regex_pattern("/\\d{11}/") is True
        assert validator.is_regex_pattern("/[a-z]+/") is True

        # 测试非正则表达式
        assert validator.is_regex_pattern("学生") is False
        assert validator.is_regex_pattern("123456") is False

    def test_validate_regex(self):
        """测试正则表达式验证"""
        validator = Validator()

        # 测试有效的正则表达式
        is_valid, error = validator.validate_regex("\\d{11}")
        assert is_valid is True
        assert error is None

        # 测试无效的正则表达式
        is_valid, error = validator.validate_regex("[invalid")
        assert is_valid is False
        assert error is not None

    def test_test_pattern(self):
        """测试模式匹配"""
        validator = Validator()

        # 测试正则表达式匹配
        is_valid, is_matched, error = validator.test_pattern("/\\d{11}/", "13812345678")
        assert is_valid is True
        assert is_matched is True
        assert error is None

        # 测试正则表达式不匹配
        is_valid, is_matched, error = validator.test_pattern("/\\d{11}/", "abc")
        assert is_valid is True
        assert is_matched is False
        assert error is None

        # 测试关键词匹配
        is_valid, is_matched, error = validator.test_pattern("学生", "我是学生")
        assert is_valid is True
        assert is_matched is True
        assert error is None

        # 测试关键词不匹配
        is_valid, is_matched, error = validator.test_pattern("学生", "我是老师")
        assert is_valid is True
        assert is_matched is False
        assert error is None


class TestConfig:
    """配置测试类"""

    def test_admin_list(self):
        """测试管理员列表"""
        config = Config({"admin_list": ["123456", "789012"]})
        assert config.admin_list == ["123456", "789012"]

        # 测试空列表
        config = Config({})
        assert config.admin_list == []

    def test_default_mode(self):
        """测试默认模式"""
        config = Config({"default_mode": "reject"})
        assert config.default_mode == "reject"

        # 测试默认值
        config = Config({})
        assert config.default_mode == "allow"

    def test_enable_logging(self):
        """测试启用日志"""
        config = Config({"enable_logging": False})
        assert config.enable_logging is False

        # 测试默认值
        config = Config({})
        assert config.enable_logging is True

    def test_is_admin(self):
        """测试管理员检查"""
        config = Config({"admin_list": ["123456"]})

        # 测试管理员
        assert config.is_admin("123456") is True

        # 测试非管理员
        assert config.is_admin("789012") is False

        # 测试空列表（所有用户都是管理员）
        config = Config({})
        assert config.is_admin("123456") is True
        assert config.is_admin("789012") is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
