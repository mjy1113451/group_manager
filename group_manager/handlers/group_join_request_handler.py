"""
加群申请处理器模块

处理加群申请事件，包括验证和通知管理员。
"""

from typing import Optional, List
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api import logger

from group_manager.core import Config, Storage, Validator, ValidationResult
from group_manager.utils import NotificationManager


class GroupJoinRequestHandler:
    """加群申请处理器类"""

    def __init__(
        self,
        plugin,
        config: Config,
        storage: Storage,
        validator: Validator,
        notification_manager: NotificationManager
    ):
        """
        初始化加群申请处理器

        Args:
            plugin: 插件实例
            config: 配置对象
            storage: 存储对象
            validator: 验证器对象
            notification_manager: 通知管理器对象
        """
        self.plugin = plugin
        self.config = config
        self.storage = storage
        self.validator = validator
        self.notification_manager = notification_manager

    async def handle_join_request(
        self,
        group_id: str,
        group_name: str,
        user_id: str,
        user_name: str,
        reason: str,
        event: Optional[AstrMessageEvent] = None
    ) -> tuple[bool, str]:
        """
        处理加群申请

        Args:
            group_id: 群ID
            group_name: 群名称
            user_id: 用户ID
            user_name: 用户名称
            reason: 申请理由
            event: 消息事件对象（可选）

        Returns:
            (是否通过, 原因)
        """
        # 获取群的配置
        rules = await self.storage.get_group_rules(group_id)
        whitelist = await self.storage.get_group_whitelist(group_id)
        blacklist = await self.storage.get_group_blacklist(group_id)

        # 验证申请
        result, matched_rules = await self.validator.validate_request(
            group_id=group_id,
            user_id=user_id,
            request_text=reason,
            rules=rules,
            whitelist=whitelist,
            blacklist=blacklist,
            default_mode=self.config.default_mode
        )

        # 记录日志
        if self.config.enable_logging:
            logger.info(
                f"[GroupManager] 加群申请验证: "
                f"群={group_name}({group_id}), "
                f"用户={user_name}({user_id}), "
                f"理由={reason}, "
                f"结果={result.value}"
            )

        # 通知管理员
        if event:
            await self.notification_manager.notify_admin(
                event=event,
                group_id=group_id,
                group_name=group_name,
                user_id=user_id,
                user_name=user_name,
                reason=reason,
                result=result,
                matched_rules=matched_rules if result == ValidationResult.ALLOW else None
            )

        # 返回结果
        if result in [ValidationResult.ALLOW, ValidationResult.WHITELISTED]:
            return True, "验证通过"
        else:
            # 构建拒绝原因
            if result == ValidationResult.BLACKLISTED:
                reject_reason = "用户在黑名单中"
            elif result == ValidationResult.REJECT:
                reject_reason = "未匹配任何验证规则"
            else:
                reject_reason = "验证失败"

            return False, reject_reason
