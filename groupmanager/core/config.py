"""
配置管理模块

负责管理插件的配置项，包括管理员列表、默认模式等。
"""

from typing import List, Optional


class Config:
    """插件配置管理类"""

    def __init__(self, config_dict: dict):
        """
        初始化配置

        Args:
            config_dict: 从 AstrBot 配置系统获取的配置字典
        """
        self.config_dict = config_dict or {}

    @property
    def admin_list(self) -> List[str]:
        """
        获取管理员ID列表

        Returns:
            管理员ID列表，如果未配置则返回空列表
        """
        return self.config_dict.get("admin_list", [])

    @property
    def default_mode(self) -> str:
        """
        获取默认模式

        Returns:
            默认模式，可选值为 "allow" 或 "reject"
        """
        return self.config_dict.get("default_mode", "allow")

    @property
    def enable_logging(self) -> bool:
        """
        获取是否启用日志

        Returns:
            是否启用日志记录
        """
        return self.config_dict.get("enable_logging", True)

    @property
    def whitelist_priority(self) -> bool:
        """
        获取白名单优先级

        Returns:
            白名单用户是否绕过规则验证直接通过
        """
        return self.config_dict.get("whitelist_priority", True)

    @property
    def blacklist_priority(self) -> bool:
        """
        获取黑名单优先级

        Returns:
            黑名单用户是否直接拒绝，即使匹配规则
        """
        return self.config_dict.get("blacklist_priority", True)

    @property
    def enable_admin_notification(self) -> bool:
        """
        获取是否启用管理员通知

        Returns:
            是否在收到加群申请时通知管理员
        """
        return self.config_dict.get("enable_admin_notification", True)

    @property
    def admin_notification_platform(self) -> str:
        """
        获取管理员通知平台

        Returns:
            通知管理员的平台类型（qq、telegram、discord等）
        """
        return self.config_dict.get("admin_notification_platform", "qq")

    @property
    def admin_notification_messages(self) -> dict:
        """
        获取通知消息模板

        Returns:
            通知消息模板字典
        """
        return self.config_dict.get("admin_notification_messages", {
            "request_received": "📢 收到新的加群申请\n\n群组: {group_name}\n申请人: {user_name}({user_id})\n申请理由: {reason}\n\n验证结果: {result}",
            "request_approved": "✅ 加群申请已通过\n\n群组: {group_name}\n申请人: {user_name}({user_id})",
            "request_rejected": "❌ 加群申请已拒绝\n\n群组: {group_name}\n申请人: {user_name}({user_id})\n原因: {reason}"
        })

    def is_admin(self, user_id: str) -> bool:
        """
        检查用户是否为管理员

        Args:
            user_id: 用户ID

        Returns:
            如果是管理员返回 True，否则返回 False
            如果未配置管理员列表，则所有用户都是管理员
        """
        # 如果没有配置管理员列表，假设所有用户都是管理员
        if not self.admin_list:
            return True

        return user_id in self.admin_list
