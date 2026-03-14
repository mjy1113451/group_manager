"""
数据存储模块

负责存储和读取插件数据，使用 AstrBot 提供的 KV 存储接口。
支持每个群独立的配置、管理员列表、规则、白名单和黑名单。
"""

from typing import List, Dict, Optional
from astrbot.api.star import Star


class Storage:
    """数据存储管理类"""

    def __init__(self, plugin: Star):
        """
        初始化存储

        Args:
            plugin: 插件实例，用于访问 KV 存储接口
        """
        self.plugin = plugin

    # ==================== 群独立配置 ====================

    async def get_group_config(self, group_id: str) -> dict:
        """获取指定群的独立配置"""
        return await self.plugin.get_kv_data(f"group_config_{group_id}", {})

    async def save_group_config(self, group_id: str, config: dict) -> None:
        """保存指定群的独立配置"""
        await self.plugin.put_kv_data(f"group_config_{group_id}", config)

    # ==================== 群启用状态 ====================

    async def is_group_enabled(self, group_id: str) -> bool:
        """检查群是否已启用插件"""
        config = await self.get_group_config(group_id)
        return config.get("enabled", False)

    async def enable_group(self, group_id: str) -> None:
        """启用群的插件功能"""
        config = await self.get_group_config(group_id)
        config["enabled"] = True
        await self.save_group_config(group_id, config)

    async def disable_group(self, group_id: str) -> None:
        """禁用群的插件功能"""
        config = await self.get_group_config(group_id)
        config["enabled"] = False
        await self.save_group_config(group_id, config)

    # ==================== 群独立管理员 ====================

    async def get_group_admins(self, group_id: str) -> List[str]:
        """获取指定群的管理员列表"""
        config = await self.get_group_config(group_id)
        return config.get("admin_list", [])

    async def add_group_admin(self, group_id: str, user_id: str) -> bool:
        """
        添加群管理员

        Returns:
            添加成功返回 True，已存在返回 False
        """
        config = await self.get_group_config(group_id)
        admins = config.get("admin_list", [])
        if user_id in admins:
            return False
        admins.append(user_id)
        config["admin_list"] = admins
        await self.save_group_config(group_id, config)
        return True

    async def remove_group_admin(self, group_id: str, user_id: str) -> bool:
        """
        移除群管理员

        Returns:
            移除成功返回 True，不存在返回 False
        """
        config = await self.get_group_config(group_id)
        admins = config.get("admin_list", [])
        if user_id not in admins:
            return False
        admins.remove(user_id)
        config["admin_list"] = admins
        await self.save_group_config(group_id, config)
        return True

    # ==================== 群独立设置 ====================

    async def get_group_setting(self, group_id: str, key: str, default=None):
        """获取群的某个独立设置项"""
        config = await self.get_group_config(group_id)
        return config.get(key, default)

    async def set_group_setting(self, group_id: str, key: str, value) -> None:
        """设置群的某个独立设置项"""
        config = await self.get_group_config(group_id)
        config[key] = value
        await self.save_group_config(group_id, config)

    # ==================== 规则管理 ====================

    async def get_group_rules(self, group_id: str) -> List[Dict]:
        """获取指定群的规则列表"""
        return await self.plugin.get_kv_data(f"rules_{group_id}", [])

    async def save_group_rules(self, group_id: str, rules: List[Dict]) -> None:
        """保存指定群的规则列表"""
        await self.plugin.put_kv_data(f"rules_{group_id}", rules)

    # ==================== 白名单管理 ====================

    async def get_group_whitelist(self, group_id: str) -> List[str]:
        """获取指定群的白名单"""
        return await self.plugin.get_kv_data(f"whitelist_{group_id}", [])

    async def save_group_whitelist(self, group_id: str, whitelist: List[str]) -> None:
        """保存指定群的白名单"""
        await self.plugin.put_kv_data(f"whitelist_{group_id}", whitelist)

    async def add_to_whitelist(self, group_id: str, user_id: str) -> bool:
        """添加用户到白名单，成功返回 True，已存在返回 False"""
        whitelist = await self.get_group_whitelist(group_id)
        if user_id in whitelist:
            return False
        whitelist.append(user_id)
        await self.save_group_whitelist(group_id, whitelist)
        return True

    async def remove_from_whitelist(self, group_id: str, user_id: str) -> bool:
        """从白名单移除用户，成功返回 True，不存在返回 False"""
        whitelist = await self.get_group_whitelist(group_id)
        if user_id not in whitelist:
            return False
        whitelist.remove(user_id)
        await self.save_group_whitelist(group_id, whitelist)
        return True

    # ==================== 黑名单管理 ====================

    async def get_group_blacklist(self, group_id: str) -> List[str]:
        """获取指定群的黑名单"""
        return await self.plugin.get_kv_data(f"blacklist_{group_id}", [])

    async def save_group_blacklist(self, group_id: str, blacklist: List[str]) -> None:
        """保存指定群的黑名单"""
        await self.plugin.put_kv_data(f"blacklist_{group_id}", blacklist)

    async def add_to_blacklist(self, group_id: str, user_id: str) -> bool:
        """添加用户到黑名单，成功返回 True，已存在返回 False"""
        blacklist = await self.get_group_blacklist(group_id)
        if user_id in blacklist:
            return False
        blacklist.append(user_id)
        await self.save_group_blacklist(group_id, blacklist)
        return True

    async def remove_from_blacklist(self, group_id: str, user_id: str) -> bool:
        """从黑名单移除用户，成功返回 True，不存在返回 False"""
        blacklist = await self.get_group_blacklist(group_id)
        if user_id not in blacklist:
            return False
        blacklist.remove(user_id)
        await self.save_group_blacklist(group_id, blacklist)
        return True
