"""
通知管理模块

负责向管理员发送加群申请通知。
使用每个群独立的管理员列表。
"""

from typing import List, Optional
from astrbot.api.event import AstrMessageEvent
from astrbot.api.star import Star
from astrbot.api import logger

from ..core import Config, Storage, ValidationResult


class NotificationManager:
    """通知管理器类"""

    def __init__(self, plugin: Star, config: Config, storage: Storage):
        """
        初始化通知管理器

        Args:
            plugin: 插件实例
            config: 配置对象（全局配置）
            storage: 存储对象（per-group 配置）
        """
        self.plugin = plugin
        self.config = config
        self.storage = storage

    async def notify_admin(
        self,
        event: AstrMessageEvent,
        group_id: str,
        group_name: str,
        user_id: str,
        user_name: str,
        reason: str,
        result: ValidationResult,
        matched_rules: Optional[List[dict]] = None
    ) -> bool:
        """通知本群管理员加群申请"""
        if not self.config.enable_admin_notification:
            return False

        # 使用该群独立的管理员列表
        admin_list = await self.storage.get_group_admins(group_id)

        if not admin_list:
            logger.info(f"[GroupManager] 群 {group_id} 未配置管理员列表，跳过通知")
            return False

        message = self._build_notification_message(
            group_name=group_name,
            user_name=user_name,
            user_id=user_id,
            reason=reason,
            result=result,
            matched_rules=matched_rules
        )

        success_count = 0
        for admin_id in admin_list:
            try:
                await self._send_private_message(admin_id, message)
                success_count += 1

                if self.config.enable_logging:
                    logger.info(
                        f"[GroupManager] 已发送通知给管理员 {admin_id}: "
                        f"群={group_name}, 用户={user_name}({user_id}), 结果={result.value}"
                    )
            except Exception as e:
                logger.error(f"[GroupManager] 发送通知给管理员 {admin_id} 失败: {str(e)}")

        return success_count > 0

    def _build_notification_message(
        self,
        group_name: str,
        user_name: str,
        user_id: str,
        reason: str,
        result: ValidationResult,
        matched_rules: Optional[List[dict]] = None
    ) -> str:
        """构建通知消息"""
        templates = self.config.admin_notification_messages

        if result == ValidationResult.WHITELISTED:
            template = templates.get("request_approved", "")
            result_text = "✅ 通过（白名单）"
        elif result == ValidationResult.BLACKLISTED:
            template = templates.get("request_rejected", "")
            result_text = "❌ 拒绝（黑名单）"
        elif result == ValidationResult.ALLOW:
            template = templates.get("request_received", "")
            result_text = "✅ 通过（匹配规则）"
        else:
            template = templates.get("request_rejected", "")
            result_text = "❌ 拒绝（未匹配规则）"

        message = template.format(
            group_name=group_name,
            user_name=user_name,
            user_id=user_id,
            reason=reason,
            result=result_text
        )

        if matched_rules and result == ValidationResult.ALLOW:
            message += "\n\n📋 匹配的规则:\n"
            for idx, rule in enumerate(matched_rules, 1):
                rule_type = "🔍 正则" if rule["type"] == "regex" else "🔑 关键词"
                message += f"{idx}. {rule_type}: {rule['content']}\n"

        return message.strip()

    async def _send_private_message(self, user_id: str, message: str) -> None:
        """发送私聊消息"""
        platform = self.config.admin_notification_platform
        unified_msg_origin = f"{platform}:{user_id}"

        from astrbot.api.message_components import Plain
        message_chain = [Plain(message)]

        await self.plugin.context.send_message(unified_msg_origin, message_chain)
