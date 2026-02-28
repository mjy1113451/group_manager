"""
通知管理模块

负责向管理员发送加群申请通知。
"""

from typing import List, Optional
from astrbot.api.event import AstrMessageEvent
from astrbot.api.star import Star
from astrbot.api import logger

from group_manager.core import Config, ValidationResult


class NotificationManager:
    """通知管理器类"""

    def __init__(self, plugin: Star, config: Config):
        """
        初始化通知管理器

        Args:
            plugin: 插件实例
            config: 配置对象
        """
        self.plugin = plugin
        self.config = config

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
        """
        通知管理员加群申请

        Args:
            event: 消息事件对象
            group_id: 群ID
            group_name: 群名称
            user_id: 用户ID
            user_name: 用户名称
            reason: 申请理由
            result: 验证结果
            matched_rules: 匹配的规则列表

        Returns:
            是否发送成功
        """
        # 检查是否启用通知
        if not self.config.enable_admin_notification:
            return False

        # 获取管理员列表
        admin_list = self.config.admin_list

        # 如果没有配置管理员列表，则不发送通知
        if not admin_list:
            logger.info("[GroupManager] 未配置管理员列表，跳过通知")
            return False

        # 构建通知消息
        message = self._build_notification_message(
            group_name=group_name,
            user_name=user_name,
            user_id=user_id,
            reason=reason,
            result=result,
            matched_rules=matched_rules
        )

        # 发送通知给所有管理员
        success_count = 0
        for admin_id in admin_list:
            try:
                # 使用私聊方式发送通知
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
        """
        构建通知消息

        Args:
            group_name: 群名称
            user_name: 用户名称
            user_id: 用户ID
            reason: 申请理由
            result: 验证结果
            matched_rules: 匹配的规则列表

        Returns:
            格式化的通知消息
        """
        # 获取消息模板
        templates = self.config.admin_notification_messages

        # 根据验证结果选择模板
        if result == ValidationResult.WHITELISTED:
            template = templates.get("request_approved", "")
            result_text = "✅ 通过（白名单）"
        elif result == ValidationResult.BLACKLISTED:
            template = templates.get("request_rejected", "")
            result_text = "❌ 拒绝（黑名单）"
        elif result == ValidationResult.ALLOW:
            template = templates.get("request_received", "")
            result_text = "✅ 通过（匹配规则）"
        else:  # REJECT
            template = templates.get("request_rejected", "")
            result_text = "❌ 拒绝（未匹配规则）"

        # 构建消息
        message = template.format(
            group_name=group_name,
            user_name=user_name,
            user_id=user_id,
            reason=reason,
            result=result_text
        )

        # 如果有匹配的规则，添加规则详情
        if matched_rules and result == ValidationResult.ALLOW:
            message += "\n\n📋 匹配的规则:\n"
            for idx, rule in enumerate(matched_rules, 1):
                rule_type = "🔍 正则" if rule["type"] == "regex" else "🔑 关键词"
                message += f"{idx}. {rule_type}: {rule['content']}\n"

        return message.strip()

    async def _send_private_message(self, user_id: str, message: str) -> None:
        """
        发送私聊消息

        Args:
            user_id: 用户ID
            message: 消息内容
        """
        # 根据平台类型发送消息
        platform = self.config.admin_notification_platform

        # 构建私聊 unified_msg_origin
        # 格式: platform_type:user_id
        unified_msg_origin = f"{platform}:{user_id}"

        # 构建消息链
        from astrbot.api.message_components import Plain
        message_chain = [Plain(message)]

        # 发送消息
        await self.plugin.context.send_message(unified_msg_origin, message_chain)
