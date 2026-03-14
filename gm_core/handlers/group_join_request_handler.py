"""
加群申请处理器模块

处理加群申请事件，包括验证和通知管理员。
仅处理已启用（通过 /gm add 自动启用）的群。
"""

from typing import Optional, List
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api import logger

from ..core import Config, Storage, Validator, ValidationResult
from ..utils import NotificationManager


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

        只处理已启用的群（通过 /gm add 自动启用或 /gm enable 手动启用）。

        Returns:
            (是否通过, 原因)
        """
        # 检查群是否已启用（per-group 状态）
        if not await self.storage.is_group_enabled(group_id):
            return True, "群未启用管理功能，默认通过"

        # 获取群的规则和名单
        rules = await self.storage.get_group_rules(group_id)
        whitelist = await self.storage.get_group_whitelist(group_id)
        blacklist = await self.storage.get_group_blacklist(group_id)

        # 获取群独立的 default_mode，若无则使用全局默认
        group_default_mode = await self.storage.get_group_setting(
            group_id, "default_mode", None
        )
        default_mode = group_default_mode if group_default_mode else self.config.default_mode

        # 验证申请
        result, matched_rules = await self.validator.validate_request(
            group_id=group_id,
            user_id=user_id,
            request_text=reason,
            rules=rules,
            whitelist=whitelist,
            blacklist=blacklist,
            default_mode=default_mode
        )

        if self.config.enable_logging:
            logger.info(
                f"[GroupManager] 加群申请验证: "
                f"群={group_name}({group_id}), "
                f"用户={user_name}({user_id}), "
                f"理由={reason}, "
                f"结果={result.value}"
            )

        # 通知本群管理员
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

        if result in [ValidationResult.ALLOW, ValidationResult.WHITELISTED]:
            return True, "验证通过"
        else:
            if result == ValidationResult.BLACKLISTED:
                reject_reason = "用户在黑名单中"
            elif result == ValidationResult.REJECT:
                reject_reason = "未匹配任何验证规则"
            else:
                reject_reason = "验证失败"
            return False, reject_reason
