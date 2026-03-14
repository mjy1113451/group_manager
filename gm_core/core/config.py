"""
配置管理模块

负责管理插件的全局配置项。
每个群的独立配置（管理员列表、启用状态等）由 Storage 模块管理。
全局配置通过 context 自动同步，修改后无需重启。
"""

from typing import List


class Config:
    """插件配置管理类（全局配置，自动同步）"""

    def __init__(self, context):
        """
        初始化配置

        Args:
            context: AstrBot 上下文对象，用于动态获取最新配置
        """
        self._context = context

    @property
    def config_dict(self) -> dict:
        """
        自动同步：每次访问都从 context 获取最新配置

        Returns:
            当前配置字典
        """
        return self._context.get_config() or {}

    @property
    def default_mode(self) -> str:
        """获取默认模式（全局默认值，可被群独立配置覆盖）"""
        return self.config_dict.get("default_mode", "allow")

    @property
    def enable_logging(self) -> bool:
        """获取是否启用日志"""
        return self.config_dict.get("enable_logging", True)

    @property
    def whitelist_priority(self) -> bool:
        """获取白名单优先级（全局默认值）"""
        return self.config_dict.get("whitelist_priority", True)

    @property
    def blacklist_priority(self) -> bool:
        """获取黑名单优先级（全局默认值）"""
        return self.config_dict.get("blacklist_priority", True)

    @property
    def enable_admin_notification(self) -> bool:
        """获取是否启用管理员通知"""
        return self.config_dict.get("enable_admin_notification", True)

    @property
    def admin_notification_platform(self) -> str:
        """获取管理员通知平台"""
        return self.config_dict.get("admin_notification_platform", "qq")

    @property
    def admin_notification_messages(self) -> dict:
        """获取通知消息模板"""
        return self.config_dict.get("admin_notification_messages", {
            "request_received": "📢 收到新的加群申请\n\n群组: {group_name}\n申请人: {user_name}({user_id})\n申请理由: {reason}\n\n验证结果: {result}",
            "request_approved": "✅ 加群申请已通过\n\n群组: {group_name}\n申请人: {user_name}({user_id})",
            "request_rejected": "❌ 加群申请已拒绝\n\n群组: {group_name}\n申请人: {user_name}({user_id})\n原因: {reason}"
        })

    @property
    def admin_group_id(self) -> str:
        """获取管理员群聊ID"""
        return self.config_dict.get("admin_group_id", "")
