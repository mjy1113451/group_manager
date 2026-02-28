"""
数据存储模块

负责存储和读取插件数据，使用 AstrBot 提供的 KV 存储接口。
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

    async def get_group_rules(self, group_id: str) -> List[Dict]:
        """
        获取指定群的规则列表

        Args:
            group_id: 群ID

        Returns:
            规则列表，如果不存在则返回空列表
        """
        return await self.plugin.get_kv_data(f"rules_{group_id}", [])

    async def save_group_rules(self, group_id: str, rules: List[Dict]) -> None:
        """
        保存指定群的规则列表

        Args:
            group_id: 群ID
            rules: 规则列表
        """
        await self.plugin.put_kv_data(f"rules_{group_id}", rules)

    async def get_group_whitelist(self, group_id: str) -> List[str]:
        """
        获取指定群的白名单

        Args:
            group_id: 群ID

        Returns:
            白名单列表，如果不存在则返回空列表
        """
        return await self.plugin.get_kv_data(f"whitelist_{group_id}", [])

    async def save_group_whitelist(self, group_id: str, whitelist: List[str]) -> None:
        """
        保存指定群的白名单

        Args:
            group_id: 群ID
            whitelist: 白名单列表
        """
        await self.plugin.put_kv_data(f"whitelist_{group_id}", whitelist)

    async def get_group_blacklist(self, group_id: str) -> List[str]:
        """
        获取指定群的黑名单

        Args:
            group_id: 群ID

        Returns:
            黑名单列表，如果不存在则返回空列表
        """
        return await self.plugin.get_kv_data(f"blacklist_{group_id}", [])

    async def save_group_blacklist(self, group_id: str, blacklist: List[str]) -> None:
        """
        保存指定群的黑名单

        Args:
            group_id: 群ID
            blacklist: 黑名单列表
        """
        await self.plugin.put_kv_data(f"blacklist_{group_id}", blacklist)

    async def add_to_whitelist(self, group_id: str, user_id: str) -> bool:
        """
        添加用户到白名单

        Args:
            group_id: 群ID
            user_id: 用户ID

        Returns:
            如果添加成功返回 True，如果已存在返回 False
        """
        whitelist = await self.get_group_whitelist(group_id)
        if user_id in whitelist:
            return False
        whitelist.append(user_id)
        await self.save_group_whitelist(group_id, whitelist)
        return True

    async def remove_from_whitelist(self, group_id: str, user_id: str) -> bool:
        """
        从白名单移除用户

        Args:
            group_id: 群ID
            user_id: 用户ID

        Returns:
            如果移除成功返回 True，如果不存在返回 False
        """
        whitelist = await self.get_group_whitelist(group_id)
        if user_id not in whitelist:
            return False
        whitelist.remove(user_id)
        await self.save_group_whitelist(group_id, whitelist)
        return True

    async def add_to_blacklist(self, group_id: str, user_id: str) -> bool:
        """
        添加用户到黑名单

        Args:
            group_id: 群ID
            user_id: 用户ID

        Returns:
            如果添加成功返回 True，如果已存在返回 False
        """
        blacklist = await self.get_group_blacklist(group_id)
        if user_id in blacklist:
            return False
        blacklist.append(user_id)
        await self.save_group_blacklist(group_id, blacklist)
        return True

    async def remove_from_blacklist(self, group_id: str, user_id: str) -> bool:
        """
        从黑名单移除用户

        Args:
            group_id: 群ID
            user_id: 用户ID

        Returns:
            如果移除成功返回 True，如果不存在返回 False
        """
        blacklist = await self.get_group_blacklist(group_id)
        if user_id not in blacklist:
            return False
        blacklist.remove(user_id)
        await self.save_group_blacklist(group_id, blacklist)
        return True
