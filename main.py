"""
GroupAdminer - 智能群管理插件

一个强大的 AstrBot 群管理插件，支持通过正则表达式、关键词、
白名单和黑名单验证加群申请。

Author: Kush-ShuL
Version: v1.0.0
License: AGPL-v3
"""

from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

from groupadminer.core import Config, Storage, Validator
from groupadminer.handlers import RuleHandler, WhitelistBlacklistHandler, GroupJoinRequestHandler
from groupadminer.utils import MessageBuilder, NotificationManager


@register(
    "groupAdminer",
    "Kush-ShuL",
    "智能群管理插件 - 支持正则表达式/关键词/白名单/黑名单验证加群申请",
    "v1.0.0"
)
class GroupAdminer(Star):
    """GroupAdminer 插件主类"""

    def __init__(self, context: Context):
        """
        初始化插件

        Args:
            context: AstrBot 上下文对象
        """
        super().__init__(context)

        # 初始化核心组件
        self.config = Config(self.get_config())
        self.storage = Storage(self)
        self.validator = Validator()

        # 初始化处理器
        self.rule_handler = RuleHandler(self, self.config, self.storage, self.validator)
        self.wb_handler = WhitelistBlacklistHandler(self, self.config, self.storage)
        self.notification_manager = NotificationManager(self, self.config)
        self.join_request_handler = GroupJoinRequestHandler(
            self, self.config, self.storage, self.validator, self.notification_manager
        )

        logger.info("[GroupAdminer] 插件已加载")

    async def initialize(self):
        """插件初始化"""
        logger.info("[GroupAdminer] 插件初始化完成")

    async def terminate(self):
        """插件销毁"""
        logger.info("[GroupAdminer] 插件已卸载")

    # ==================== 指令组 ====================

    @filter.command_group("ga")
    async def ga(self):
        """群管理器指令组"""
        pass

    # ==================== 规则管理指令 ====================

    @ga.command("add")
    async def ga_add(self, event: AstrMessageEvent, pattern: str = None):
        """
        添加关键词/正则表达式规则
        用法: /ga add [关键词|正则表达式]
        """
        async for result in self.rule_handler.add_rule(event, pattern):
            yield result

    @ga.command("remove")
    async def ga_remove(self, event: AstrMessageEvent, index: int = None):
        """
        删除指定索引的规则
        用法: /ga remove [索引]
        """
        async for result in self.rule_handler.remove_rule(event, index):
            yield result

    @ga.command("list")
    async def ga_list(self, event: AstrMessageEvent):
        """
        查看当前群的所有规则
        用法: /ga list
        """
        async for result in self.rule_handler.list_rules(event):
            yield result

    @ga.command("clear")
    async def ga_clear(self, event: AstrMessageEvent):
        """
        清空当前群的所有规则
        用法: /ga clear
        """
        async for result in self.rule_handler.clear_rules(event):
            yield result

    @ga.command("test")
    async def ga_test(self, event: AstrMessageEvent, test_text: str = None):
        """
        测试文本是否匹配当前群的规则
        用法: /ga test [测试文本]
        """
        async for result in self.rule_handler.test_rule(event, test_text):
            yield result

    # ==================== 白名单指令 ====================

    @ga.group("whitelist")
    async def ga_whitelist(self):
        """白名单管理指令组"""
        pass

    @ga_whitelist.command("add")
    async def ga_whitelist_add(self, event: AstrMessageEvent, user_id: str = None):
        """
        添加用户到白名单
        用法: /ga whitelist add [用户ID]
        """
        async for result in self.wb_handler.whitelist_add(event, user_id):
            yield result

    @ga_whitelist.command("remove")
    async def ga_whitelist_remove(self, event: AstrMessageEvent, user_id: str = None):
        """
        从白名单移除用户
        用法: /ga whitelist remove [用户ID]
        """
        async for result in self.wb_handler.whitelist_remove(event, user_id):
            yield result

    @ga_whitelist.command("list")
    async def ga_whitelist_list(self, event: AstrMessageEvent):
        """
        查看白名单
        用法: /ga whitelist list
        """
        async for result in self.wb_handler.whitelist_list(event):
            yield result

    # ==================== 黑名单指令 ====================

    @ga.group("blacklist")
    async def ga_blacklist(self):
        """黑名单管理指令组"""
        pass

    @ga_blacklist.command("add")
    async def ga_blacklist_add(self, event: AstrMessageEvent, user_id: str = None):
        """
        添加用户到黑名单
        用法: /ga blacklist add [用户ID]
        """
        async for result in self.wb_handler.blacklist_add(event, user_id):
            yield result

    @ga_blacklist.command("remove")
    async def ga_blacklist_remove(self, event: AstrMessageEvent, user_id: str = None):
        """
        从黑名单移除用户
        用法: /ga blacklist remove [用户ID]
        """
        async for result in self.wb_handler.blacklist_remove(event, user_id):
            yield result

    @ga_blacklist.command("list")
    async def ga_blacklist_list(self, event: AstrMessageEvent):
        """
        查看黑名单
        用法: /ga blacklist list
        """
        async for result in self.wb_handler.blacklist_list(event):
            yield result

    # ==================== 帮助指令 ====================

    @ga.command("help", alias={"帮助"})
    async def ga_help(self, event: AstrMessageEvent):
        """
        显示帮助信息
        用法: /ga help
        """
        yield event.plain_result(MessageBuilder.build_help_message())

    # ==================== 测试指令 ====================

    @ga.command("test_join")
    async def ga_test_join(self, event: AstrMessageEvent, user_id: str = None, reason: str = None):
        """
        测试加群申请（模拟收到加群申请）
        用法: /ga test_join [用户ID] [申请理由]
        """
        # 检查是否在群聊中
        if not event.message_obj.group_id:
            yield event.plain_result(MessageBuilder.error("此指令仅限群聊使用"))
            return

        # 检查参数
        if user_id is None or reason is None:
            yield event.plain_result(
                MessageBuilder.error("请提供用户ID和申请理由\n\n用法: /ga test_join [用户ID] [申请理由]")
            )
            return

        # 检查管理员权限
        if not is_admin(event, self.config):
            yield event.plain_result(MessageBuilder.admin_required(event))
            return

        # 处理加群申请
        group_id = event.message_obj.group_id
        group_name = event.message_obj.group_id  # 这里使用群ID作为群名，实际应该获取群名称

        approved, reason_msg = await self.join_request_handler.handle_join_request(
            group_id=group_id,
            group_name=group_name,
            user_id=user_id,
            user_name=user_id,
            reason=reason,
            event=event
        )

        # 返回测试结果
        if approved:
            yield event.plain_result(
                MessageBuilder.success(
                    f"测试加群申请通过\n\n"
                    f"📝 用户ID: {user_id}\n"
                    f"💬 申请理由: {reason}\n"
                    f"✅ 结果: {reason_msg}\n\n"
                    f"📢 已通知管理员"
                )
            )
        else:
            yield event.plain_result(
                MessageBuilder.warning(
                    f"测试加群申请拒绝\n\n"
                    f"📝 用户ID: {user_id}\n"
                    f"💬 申请理由: {reason}\n"
                    f"❌ 原因: {reason_msg}\n\n"
                    f"📢 已通知管理员"
                )
            )

