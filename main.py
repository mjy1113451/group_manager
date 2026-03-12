from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

from .gm_core.core import Config, Storage, Validator
from .gm_core.handlers import RuleHandler, WhitelistBlacklistHandler, GroupJoinRequestHandler
from .gm_core.utils import MessageBuilder, NotificationManager, is_admin


@register("astrbot_plugin_group_manager", "mjy1113451", "智能群管理插件 - 支持正则表达式/关键词/白名单/黑名单验证加群申请", "v1.1.0")
class GroupManager(Star):
    """GroupManager 插件主类"""

    def __init__(self, context: Context, config: dict = None):
        super().__init__(context)

        self.MessageBuilder = MessageBuilder

        self.config = Config(self.context)
        self.storage = Storage(self)
        self.validator = Validator()

        self.notification_manager = NotificationManager(self, self.config, self.storage)

        self.rule_handler = RuleHandler(self, self.config, self.storage, self.validator)
        self.wb_handler = WhitelistBlacklistHandler(self, self.config, self.storage)
        self.join_request_handler = GroupJoinRequestHandler(
            self, self.config, self.storage, self.validator, self.notification_manager
        )

        logger.info("[GroupManager] 插件已加载")

    async def initialize(self):
        """插件初始化"""
        logger.info("[GroupManager] 插件初始化完成")

    async def terminate(self):
        """插件销毁"""
        logger.info("[GroupManager] 插件已卸载")

    # ==================== 指令组 ====================

    @filter.command_group("gm")
    async def gm(self):
        """群管理器指令组"""
        pass

    # ==================== 规则管理指令 ====================

    @gm.command("add")
    async def gm_add(self, event: AstrMessageEvent, pattern: str = None):
        """ 添加关键词/正则表达式规则（自动启用本群） 用法: /gm add [关键词|正则表达式] """
        async for result in self.rule_handler.add_rule(event, pattern):
            yield result

    @gm.command("remove")
    async def gm_remove(self, event: AstrMessageEvent, index: int = None):
        """ 删除指定索引的规则 用法: /gm remove [索引] """
        async for result in self.rule_handler.remove_rule(event, index):
            yield result

    @gm.command("list")
    async def gm_list(self, event: AstrMessageEvent):
        """ 查看当前群的所有规则 用法: /gm list """
        async for result in self.rule_handler.list_rules(event):
            yield result

    @gm.command("clear")
    async def gm_clear(self, event: AstrMessageEvent):
        """ 清空当前群的所有规则 用法: /gm clear """
        async for result in self.rule_handler.clear_rules(event):
            yield result

    @gm.command("test")
    async def gm_test(self, event: AstrMessageEvent, test_text: str = None):
        """ 测试文本是否匹配当前群的规则 用法: /gm test [测试文本] """
        async for result in self.rule_handler.test_rule(event, test_text):
            yield result

    # ==================== 管理员管理指令 ====================

    @gm.group("admin")
    async def gm_admin(self):
        """管理员管理指令组"""
        pass

    @gm_admin.command("add")
    async def gm_admin_add(self, event: AstrMessageEvent, user_id: str = None):
        """ 添加本群管理员 用法: /gm admin add [用户ID] """
        if not event.message_obj.group_id:
            yield event.plain_result(self.MessageBuilder.error("此指令仅限群聊使用"))
            return

        if user_id is None:
            yield event.plain_result(
                self.MessageBuilder.error("请提供用户ID\n\n用法: /gm admin add [用户ID]")
            )
            return

        if not await is_admin(event, self.storage):
            yield event.plain_result(self.MessageBuilder.admin_required(event))
            return

        group_id = event.message_obj.group_id
        success = await self.storage.add_group_admin(group_id, user_id)

        if success:
            if self.config.enable_logging:
                logger.info(
                    f"[GroupManager] 群 {group_id} 添加管理员: "
                    f"用户ID={user_id}, 操作者={event.get_sender_id()}"
                )
            yield event.plain_result(
                self.MessageBuilder.success(f"已将用户 {user_id} 添加为本群管理员")
            )
        else:
            yield event.plain_result(
                self.MessageBuilder.warning(f"用户 {user_id} 已是本群管理员")
            )

    @gm_admin.command("remove")
    async def gm_admin_remove(self, event: AstrMessageEvent, user_id: str = None):
        """ 移除本群管理员 用法: /gm admin remove [用户ID] """
        if not event.message_obj.group_id:
            yield event.plain_result(self.MessageBuilder.error("此指令仅限群聊使用"))
            return

        if user_id is None:
            yield event.plain_result(
                self.MessageBuilder.error("请提供用户ID\n\n用法: /gm admin remove [用户ID]")
            )
            return

        if not await is_admin(event, self.storage):
            yield event.plain_result(self.MessageBuilder.admin_required(event))
            return

        group_id = event.message_obj.group_id
        success = await self.storage.remove_group_admin(group_id, user_id)

        if success:
            if self.config.enable_logging:
                logger.info(
                    f"[GroupManager] 群 {group_id} 移除管理员: "
                    f"用户ID={user_id}, 操作者={event.get_sender_id()}"
                )
            yield event.plain_result(
                self.MessageBuilder.success(f"已将用户 {user_id} 从本群管理员移除")
            )
        else:
            yield event.plain_result(
                self.MessageBuilder.warning(f"用户 {user_id} 不是本群管理员")
            )

    @gm_admin.command("list")
    async def gm_admin_list(self, event: AstrMessageEvent):
        """ 查看本群管理员列表 用法: /gm admin list """
        if not event.message_obj.group_id:
            yield event.plain_result(self.MessageBuilder.error("此指令仅限群聊使用"))
            return

        group_id = event.message_obj.group_id
        admins = await self.storage.get_group_admins(group_id)
        yield event.plain_result(self.MessageBuilder.build_admin_list(admins))

    # ==================== 群启用/禁用指令 ====================

    @gm.command("enable")
    async def gm_enable(self, event: AstrMessageEvent):
        """ 启用本群的群管理功能 用法: /gm enable """
        if not event.message_obj.group_id:
            yield event.plain_result(self.MessageBuilder.error("此指令仅限群聊使用"))
            return

        if not await is_admin(event, self.storage):
            yield event.plain_result(self.MessageBuilder.admin_required(event))
            return

        group_id = event.message_obj.group_id
        if await self.storage.is_group_enabled(group_id):
            yield event.plain_result(self.MessageBuilder.warning("本群已启用群管理功能"))
            return

        await self.storage.enable_group(group_id)
        logger.info(f"[GroupManager] 群 {group_id} 已启用, 操作者={event.get_sender_id()}")
        yield event.plain_result(
            self.MessageBuilder.success("已启用本群的群管理功能")
        )

    @gm.command("disable")
    async def gm_disable(self, event: AstrMessageEvent):
        """ 禁用本群的群管理功能 用法: /gm disable """
        if not event.message_obj.group_id:
            yield event.plain_result(self.MessageBuilder.error("此指令仅限群聊使用"))
            return

        if not await is_admin(event, self.storage):
            yield event.plain_result(self.MessageBuilder.admin_required(event))
            return

        group_id = event.message_obj.group_id
        if not await self.storage.is_group_enabled(group_id):
            yield event.plain_result(self.MessageBuilder.warning("本群未启用群管理功能"))
            return

        await self.storage.disable_group(group_id)
        logger.info(f"[GroupManager] 群 {group_id} 已禁用, 操作者={event.get_sender_id()}")
        yield event.plain_result(
            self.MessageBuilder.success("已禁用本群的群管理功能")
        )

    # ==================== 白名单指令 ====================

    @gm.group("whitelist")
    async def gm_whitelist(self):
        """白名单管理指令组"""
        pass

    @gm_whitelist.command("add")
    async def gm_whitelist_add(self, event: AstrMessageEvent, user_id: str = None):
        """ 添加用户到白名单 用法: /gm whitelist add [用户ID] """
        async for result in self.wb_handler.whitelist_add(event, user_id):
            yield result

    @gm_whitelist.command("remove")
    async def gm_whitelist_remove(self, event: AstrMessageEvent, user_id: str = None):
        """ 从白名单移除用户 用法: /gm whitelist remove [用户ID] """
        async for result in self.wb_handler.whitelist_remove(event, user_id):
            yield result

    @gm_whitelist.command("list")
    async def gm_whitelist_list(self, event: AstrMessageEvent):
        """ 查看白名单 用法: /gm whitelist list """
        async for result in self.wb_handler.whitelist_list(event):
            yield result

    # ==================== 黑名单指令 ====================

    @gm.group("blacklist")
    async def gm_blacklist(self):
        """黑名单管理指令组"""
        pass

    @gm_blacklist.command("add")
    async def gm_blacklist_add(self, event: AstrMessageEvent, user_id: str = None):
        """ 添加用户到黑名单 用法: /gm blacklist add [用户ID] """
        async for result in self.wb_handler.blacklist_add(event, user_id):
            yield result

    @gm_blacklist.command("remove")
    async def gm_blacklist_remove(self, event: AstrMessageEvent, user_id: str = None):
        """ 从黑名单移除用户 用法: /gm blacklist remove [用户ID] """
        async for result in self.wb_handler.blacklist_remove(event, user_id):
            yield result

    @gm_blacklist.command("list")
    async def gm_blacklist_list(self, event: AstrMessageEvent):
        """ 查看黑名单 用法: /gm blacklist list """
        async for result in self.wb_handler.blacklist_list(event):
            yield result

    # ==================== 帮助指令 ====================

    @gm.command("help", alias={"帮助"})
    async def gm_help(self, event: AstrMessageEvent):
        """ 显示帮助信息 用法: /gm help """
        yield event.plain_result(self.MessageBuilder.build_help_message())
