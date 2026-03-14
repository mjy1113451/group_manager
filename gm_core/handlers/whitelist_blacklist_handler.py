"""
白名单/黑名单处理器模块

处理白名单和黑名单相关的指令。
"""

from typing import Optional
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api import logger

from ..core import Config, Storage
from ..utils import MessageBuilder, is_admin


class WhitelistBlacklistHandler:
    """白名单/黑名单处理器类"""

    def __init__(self, plugin, config: Config, storage: Storage):
        self.plugin = plugin
        self.config = config
        self.storage = storage

    async def whitelist_add(self, event: AstrMessageEvent, user_id: Optional[str] = None):
        """添加用户到白名单"""
        if not event.message_obj.group_id:
            yield event.plain_result(MessageBuilder.error("此指令仅限群聊使用"))
            return

        if user_id is None:
            yield event.plain_result(
                MessageBuilder.error("请提供用户ID\n\n用法: /gm whitelist add [用户ID]")
            )
            return

        if not await is_admin(event, self.storage):
            yield event.plain_result(MessageBuilder.admin_required(event))
            return

        group_id = event.message_obj.group_id
        success = await self.storage.add_to_whitelist(group_id, user_id)

        if success:
            if self.config.enable_logging:
                logger.info(
                    f"[GroupManager] 群 {group_id} 添加白名单: "
                    f"用户ID={user_id}, 操作者={event.get_sender_id()}"
                )
            yield event.plain_result(
                MessageBuilder.success(f"已将用户 {user_id} 添加到白名单")
            )
        else:
            yield event.plain_result(
                MessageBuilder.warning(f"用户 {user_id} 已在白名单中")
            )

    async def whitelist_remove(self, event: AstrMessageEvent, user_id: Optional[str] = None):
        """从白名单移除用户"""
        if not event.message_obj.group_id:
            yield event.plain_result(MessageBuilder.error("此指令仅限群聊使用"))
            return

        if user_id is None:
            yield event.plain_result(
                MessageBuilder.error("请提供用户ID\n\n用法: /gm whitelist remove [用户ID]")
            )
            return

        if not await is_admin(event, self.storage):
            yield event.plain_result(MessageBuilder.admin_required(event))
            return

        group_id = event.message_obj.group_id
        success = await self.storage.remove_from_whitelist(group_id, user_id)

        if success:
            if self.config.enable_logging:
                logger.info(
                    f"[GroupManager] 群 {group_id} 移除白名单: "
                    f"用户ID={user_id}, 操作者={event.get_sender_id()}"
                )
            yield event.plain_result(
                MessageBuilder.success(f"已将用户 {user_id} 从白名单移除")
            )
        else:
            yield event.plain_result(
                MessageBuilder.warning(f"用户 {user_id} 不在白名单中")
            )

    async def whitelist_list(self, event: AstrMessageEvent):
        """查看白名单"""
        if not event.message_obj.group_id:
            yield event.plain_result(MessageBuilder.error("此指令仅限群聊使用"))
            return

        group_id = event.message_obj.group_id
        whitelist = await self.storage.get_group_whitelist(group_id)
        yield event.plain_result(MessageBuilder.build_whitelist_list(whitelist))

    async def blacklist_add(self, event: AstrMessageEvent, user_id: Optional[str] = None):
        """添加用户到黑名单"""
        if not event.message_obj.group_id:
            yield event.plain_result(MessageBuilder.error("此指令仅限群聊使用"))
            return

        if user_id is None:
            yield event.plain_result(
                MessageBuilder.error("请提供用户ID\n\n用法: /gm blacklist add [用户ID]")
            )
            return

        if not await is_admin(event, self.storage):
            yield event.plain_result(MessageBuilder.admin_required(event))
            return

        group_id = event.message_obj.group_id
        success = await self.storage.add_to_blacklist(group_id, user_id)

        if success:
            if self.config.enable_logging:
                logger.info(
                    f"[GroupManager] 群 {group_id} 添加黑名单: "
                    f"用户ID={user_id}, 操作者={event.get_sender_id()}"
                )
            yield event.plain_result(
                MessageBuilder.success(f"已将用户 {user_id} 添加到黑名单")
            )
        else:
            yield event.plain_result(
                MessageBuilder.warning(f"用户 {user_id} 已在黑名单中")
            )

    async def blacklist_remove(self, event: AstrMessageEvent, user_id: Optional[str] = None):
        """从黑名单移除用户"""
        if not event.message_obj.group_id:
            yield event.plain_result(MessageBuilder.error("此指令仅限群聊使用"))
            return

        if user_id is None:
            yield event.plain_result(
                MessageBuilder.error("请提供用户ID\n\n用法: /gm blacklist remove [用户ID]")
            )
            return

        if not await is_admin(event, self.storage):
            yield event.plain_result(MessageBuilder.admin_required(event))
            return

        group_id = event.message_obj.group_id
        success = await self.storage.remove_from_blacklist(group_id, user_id)

        if success:
            if self.config.enable_logging:
                logger.info(
                    f"[GroupManager] 群 {group_id} 移除黑名单: "
                    f"用户ID={user_id}, 操作者={event.get_sender_id()}"
                )
            yield event.plain_result(
                MessageBuilder.success(f"已将用户 {user_id} 从黑名单移除")
            )
        else:
            yield event.plain_result(
                MessageBuilder.warning(f"用户 {user_id} 不在黑名单中")
            )

    async def blacklist_list(self, event: AstrMessageEvent):
        """查看黑名单"""
        if not event.message_obj.group_id:
            yield event.plain_result(MessageBuilder.error("此指令仅限群聊使用"))
            return

        group_id = event.message_obj.group_id
        blacklist = await self.storage.get_group_blacklist(group_id)
        yield event.plain_result(MessageBuilder.build_blacklist_list(blacklist))
