"""
消息构建器模块

负责构建各种类型的精美消息。
"""

from typing import List, Dict
from astrbot.api.event import AstrMessageEvent
from astrbot.api.message_components import At, Plain


class MessageBuilder:
    """消息构建器类"""

    @staticmethod
    def success(content: str) -> str:
        """
        构建成功消息

        Args:
            content: 消息内容

        Returns:
            格式化后的成功消息
        """
        return f"✨ {content}"

    @staticmethod
    def error(content: str) -> str:
        """
        构建错误消息

        Args:
            content: 消息内容

        Returns:
            格式化后的错误消息
        """
        return f"❌ {content}"

    @staticmethod
    def warning(content: str) -> str:
        """
        构建警告消息

        Args:
            content: 消息内容

        Returns:
            格式化后的警告消息
        """
        return f"⚠️ {content}"

    @staticmethod
    def info(content: str) -> str:
        """
        构建信息消息

        Args:
            content: 消息内容

        Returns:
            格式化后的信息消息
        """
        return f"ℹ️ {content}"

    @staticmethod
    def admin_required(event: AstrMessageEvent) -> str:
        """
        构建需要管理员权限的消息

        Args:
            event: 消息事件

        Returns:
            格式化后的权限提示消息
        """
        return (
            f"🔒 {At(qq=event.get_sender_id())}\n"
            f"❌ 此指令仅限管理员使用\n\n"
            f"💡 请联系群管理员或配置管理员列表"
        )

    @staticmethod
    def build_rules_list(rules: List[Dict]) -> str:
        """
        构建规则列表消息

        Args:
            rules: 规则列表

        Returns:
            格式化后的规则列表
        """
        if not rules:
            return MessageBuilder.warning("当前群没有任何规则")

        message_parts = [
            "📋 当前群规则列表\n",
            "=" * 40 + "\n"
        ]

        for idx, rule in enumerate(rules, 1):
            rule_type = "🔍 正则" if rule["type"] == "regex" else "🔑 关键词"
            message_parts.append(f"{idx}. {rule_type}\n")
            message_parts.append(f"   内容: {rule['content']}\n")
            message_parts.append(f"   创建者: {rule['created_by']}\n")
            message_parts.append(f"   时间: {rule['created_at']}\n")
            message_parts.append("-" * 40 + "\n")

        message_parts.append(f"📊 总计: {len(rules)} 条规则")
        message_parts.append(f"\n💡 使用 /gm remove [索引] 删除规则")

        return "".join(message_parts)

    @staticmethod
    def build_whitelist_list(whitelist: List[str]) -> str:
        """
        构建白名单列表消息

        Args:
            whitelist: 白名单列表

        Returns:
            格式化后的白名单列表
        """
        if not whitelist:
            return MessageBuilder.warning("当前群白名单为空")

        message_parts = [
            "📋 当前群白名单\n",
            "=" * 40 + "\n"
        ]

        for idx, user_id in enumerate(whitelist, 1):
            message_parts.append(f"{idx}. {user_id}\n")

        message_parts.append(f"\n📊 总计: {len(whitelist)} 人")

        return "".join(message_parts)

    @staticmethod
    def build_blacklist_list(blacklist: List[str]) -> str:
        """
        构建黑名单列表消息

        Args:
            blacklist: 黑名单列表

        Returns:
            格式化后的黑名单列表
        """
        if not blacklist:
            return MessageBuilder.warning("当前群黑名单为空")

        message_parts = [
            "📋 当前群黑名单\n",
            "=" * 40 + "\n"
        ]

        for idx, user_id in enumerate(blacklist, 1):
            message_parts.append(f"{idx}. {user_id}\n")

        message_parts.append(f"\n📊 总计: {len(blacklist)} 人")

        return "".join(message_parts)

    @staticmethod
    def build_test_result(
        test_text: str,
        matched: bool,
        matched_rules: List[Dict]
    ) -> str:
        """
        构建测试结果消息

        Args:
            test_text: 测试文本
            matched: 是否匹配
            matched_rules: 匹配的规则列表

        Returns:
            格式化后的测试结果
        """
        if matched:
            message_parts = [
                "✅ 测试通过\n",
                "=" * 40 + "\n",
                f"📝 测试文本: {test_text}\n",
                f"✨ 匹配到 {len(matched_rules)} 条规则:\n\n"
            ]

            for idx, rule in enumerate(matched_rules, 1):
                rule_type = "🔍 正则" if rule["type"] == "regex" else "🔑 关键词"
                message_parts.append(f"{idx}. {rule_type}: {rule['content']}\n")

            message_parts.append(f"\n🎉 该加群申请将被允许！")
        else:
            message_parts = [
                "❌ 测试失败\n",
                "=" * 40 + "\n",
                f"📝 测试文本: {test_text}\n",
                f"⚠️ 未匹配到任何规则\n",
                f"🚫 该加群申请将被拒绝！"
            ]

        return "".join(message_parts)

    @staticmethod
    def build_help_message() -> str:
        """
        构建帮助消息

        Returns:
            格式化后的帮助消息
        """
        return """🤖 GroupManager 群管理器帮助

📌 功能介绍
本插件支持通过关键词、正则表达式、白名单和黑名单验证加群申请。

💻 指令列表

🔧 /gm add [关键词|正则表达式]
   添加关键词或正则表达式规则
   示例:
   - /gm add 学生
   - /gm add /\\d{11}/  (手机号正则)

🔨 /gm remove [索引]
   删除指定索引的规则
   示例: /gm remove 1

📋 /gm list
   查看当前群的所有规则

🗑️ /gm clear
   清空当前群的所有规则

🧪 /gm test [测试文本]
   测试文本是否匹配规则
   示例: /gm test 我是学生

⚪ /gm whitelist add [用户ID]
   添加用户到白名单
   示例: /gm whitelist add 123456

⚫ /gm blacklist add [用户ID]
   添加用户到黑名单
   示例: /gm blacklist add 123456

⚪ /gm whitelist remove [用户ID]
   从白名单移除用户
   示例: /gm whitelist remove 123456

⚫ /gm blacklist remove [用户ID]
   从黑名单移除用户
   示例: /gm blacklist remove 123456

📋 /gm whitelist list
   查看白名单

📋 /gm blacklist list
   查看黑名单

❓ /gm help
   显示此帮助信息

💡 使用提示
- 正则表达式请使用 // 包裹
- 关键词支持部分匹配
- 白名单优先级最高，白名单用户直接通过
- 黑名单优先级次之，黑名单用户直接拒绝
- 只有管理员可以添加/删除规则和白名单/黑名单
- 所有成员都可以查看和测试规则

📚 正则表达式示例
- 手机号: /\\d{11}/
- QQ号: /[1-9][0-9]{4,}/
- 邮箱: /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}/
- 学号: /\\d{8,12}/
- 身份证: /\\d{17}[\\dXx]/

⚙️ 开发者: Kush-ShuL
🔗 项目: https://github.com/Kush-ShuL/GroupManager"""

