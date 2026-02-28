"""
规则处理器模块

处理规则相关的指令，包括添加、删除、查看、清空和测试规则。
"""

from typing import Optional
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api import logger

from group_manager.core import Config, Storage, Validator, RuleType
from group_manager.utils import MessageBuilder, is_admin


class RuleHandler:
    """规则处理器类"""

    def __init__(self, plugin, config: Config, storage: Storage, validator: Validator):
        """
        初始化规则处理器

        Args:
            plugin: 插件实例
            config: 配置对象
            storage: 存储对象
            validator: 验证器对象
        """
        self.plugin = plugin
        self.config = config
        self.storage = storage
        self.validator = validator

    async def add_rule(self, event: AstrMessageEvent, pattern: Optional[str] = None):
        """
        添加关键词/正则表达式规则

        Args:
            event: 消息事件
            pattern: 关键词或正则表达式
        """
        # 检查是否在群聊中
        if not event.message_obj.group_id:
            yield event.plain_result(MessageBuilder.error("此指令仅限群聊使用"))
            return

        # 检查参数
        if pattern is None:
            yield event.plain_result(
                MessageBuilder.error("请提供关键词或正则表达式\n\n"
                                    "用法: /ga add [关键词|正则表达式]\n"
                                    "正则表达式请使用 // 包裹，例如: /ga add /\\d{11}/")
            )
            return

        # 检查管理员权限
        if not is_admin(event, self.config):
            yield event.plain_result(MessageBuilder.admin_required(event))
            return

        # 判断是否为正则表达式
        is_regex = self.validator.is_regex_pattern(pattern)

        if is_regex:
            # 验证正则表达式
            regex_pattern = pattern[1:-1]
            is_valid, error = self.validator.validate_regex(regex_pattern)
            if not is_valid:
                yield event.plain_result(MessageBuilder.error(f"正则表达式无效: {error}"))
                return
            pattern_type = RuleType.REGEX
            content = regex_pattern
        else:
            pattern_type = RuleType.KEYWORD
            content = pattern

        # 获取当前群的规则列表
        group_id = event.message_obj.group_id
        group_rules = await self.storage.get_group_rules(group_id)

        # 添加新规则
        new_rule = {
            "type": pattern_type.value,
            "content": content,
            "created_by": event.get_sender_id(),
            "created_at": event.message_obj.timestamp
        }
        group_rules.append(new_rule)

        # 保存规则
        await self.storage.save_group_rules(group_id, group_rules)

        # 记录日志
        if self.config.enable_logging:
            logger.info(
                f"[GroupManager] 群 {group_id} 添加规则: "
                f"类型={pattern_type.value}, 内容={content}, "
                f"操作者={event.get_sender_id()}"
            )

        # 返回成功消息
        rule_count = len(group_rules)
        yield event.plain_result(
            MessageBuilder.success(
                f"成功添加{'正则表达式' if is_regex else '关键词'}规则\n"
                f"📝 内容: {content}\n"
                f"📊 当前群规则总数: {rule_count}"
            )
        )

    async def remove_rule(self, event: AstrMessageEvent, index: Optional[int] = None):
        """
        删除指定索引的规则

        Args:
            event: 消息事件
            index: 规则索引
        """
        # 检查是否在群聊中
        if not event.message_obj.group_id:
            yield event.plain_result(MessageBuilder.error("此指令仅限群聊使用"))
            return

        # 检查参数
        if index is None:
            yield event.plain_result(
                MessageBuilder.error("请提供要删除的规则索引\n\n用法: /ga remove [索引]")
            )
            return

        # 检查管理员权限
        if not is_admin(event, self.config):
            yield event.plain_result(MessageBuilder.admin_required(event))
            return

        # 获取当前群的规则列表
        group_id = event.message_obj.group_id
        group_rules = await self.storage.get_group_rules(group_id)

        if not group_rules:
            yield event.plain_result(MessageBuilder.warning("当前群没有任何规则"))
            return

        # 检查索引是否有效
        if index < 1 or index > len(group_rules):
            yield event.plain_result(
                MessageBuilder.error(f"索引无效，请输入 1-{len(group_rules)} 之间的数字")
            )
            return

        # 删除规则
        removed_rule = group_rules.pop(index - 1)

        # 保存规则
        await self.storage.save_group_rules(group_id, group_rules)

        # 记录日志
        if self.config.enable_logging:
            logger.info(
                f"[GroupManager] 群 {group_id} 删除规则: "
                f"类型={removed_rule['type']}, 内容={removed_rule['content']}, "
                f"操作者={event.get_sender_id()}"
            )

        # 返回成功消息
        yield event.plain_result(
            MessageBuilder.success(
                f"成功删除规则\n"
                f"📝 类型: {'正则表达式' if removed_rule['type'] == 'regex' else '关键词'}\n"
                f"🎯 内容: {removed_rule['content']}\n"
                f"📊 剩余规则数: {len(group_rules)}"
            )
        )

    async def list_rules(self, event: AstrMessageEvent):
        """
        查看当前群的所有规则

        Args:
            event: 消息事件
        """
        # 检查是否在群聊中
        if not event.message_obj.group_id:
            yield event.plain_result(MessageBuilder.error("此指令仅限群聊使用"))
            return

        # 获取当前群的规则列表
        group_id = event.message_obj.group_id
        group_rules = await self.storage.get_group_rules(group_id)

        # 构建规则列表消息
        if not group_rules:
            yield event.plain_result(
                MessageBuilder.warning("当前群没有任何规则\n\n"
                                      "💡 使用 /ga add [关键词|正则表达式] 添加规则")
            )
        else:
            yield event.plain_result(MessageBuilder.build_rules_list(group_rules))

    async def clear_rules(self, event: AstrMessageEvent):
        """
        清空当前群的所有规则

        Args:
            event: 消息事件
        """
        # 检查是否在群聊中
        if not event.message_obj.group_id:
            yield event.plain_result(MessageBuilder.error("此指令仅限群聊使用"))
            return

        # 检查管理员权限
        if not is_admin(event, self.config):
            yield event.plain_result(MessageBuilder.admin_required(event))
            return

        # 获取当前群的规则列表
        group_id = event.message_obj.group_id
        group_rules = await self.storage.get_group_rules(group_id)

        if not group_rules:
            yield event.plain_result(MessageBuilder.warning("当前群没有任何规则"))
            return

        # 清空规则
        await self.storage.save_group_rules(group_id, [])

        # 记录日志
        if self.config.enable_logging:
            logger.info(
                f"[GroupManager] 群 {group_id} 清空所有规则, "
                f"共删除 {len(group_rules)} 条规则, 操作者={event.get_sender_id()}"
            )

        # 返回成功消息
        yield event.plain_result(
            MessageBuilder.success(f"已清空当前群的所有规则\n🗑️ 共删除 {len(group_rules)} 条规则")
        )

    async def test_rule(self, event: AstrMessageEvent, test_text: Optional[str] = None):
        """
        测试文本是否匹配当前群的规则

        Args:
            event: 消息事件
            test_text: 测试文本
        """
        # 检查是否在群聊中
        if not event.message_obj.group_id:
            yield event.plain_result(MessageBuilder.error("此指令仅限群聊使用"))
            return

        # 检查参数
        if test_text is None:
            yield event.plain_result(
                MessageBuilder.error("请提供测试文本\n\n用法: /ga test [测试文本]")
            )
            return

        # 获取当前群的规则列表
        group_id = event.message_obj.group_id
        group_rules = await self.storage.get_group_rules(group_id)

        if not group_rules:
            yield event.plain_result(
                MessageBuilder.warning("当前群没有任何规则\n\n"
                                      "💡 使用 /ga add [关键词|正则表达式] 添加规则")
            )
            return

        # 测试匹配
        matched_rules = []

        for rule in group_rules:
            if rule["type"] == RuleType.REGEX.value:
                try:
                    if self.validator.test_pattern(rule["content"], test_text)[1]:
                        matched_rules.append(rule)
                except Exception:
                    continue
            elif rule["type"] == RuleType.KEYWORD.value:
                if rule["content"] in test_text:
                    matched_rules.append(rule)

        # 构建测试结果消息
        matched = len(matched_rules) > 0
        yield event.plain_result(MessageBuilder.build_test_result(test_text, matched, matched_rules))
