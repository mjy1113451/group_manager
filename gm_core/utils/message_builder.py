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
        return f"✨ {content}"

    @staticmethod
    def error(content: str) -> str:
        return f"❌ {content}"

    @staticmethod
    def warning(content: str) -> str:
        return f"⚠️ {content}"

    @staticmethod
    def info(content: str) -> str:
        return f"ℹ️ {content}"

    @staticmethod
    def admin_required(event: AstrMessageEvent) -> str:
        return (
            f"🔒 {At(qq=event.get_sender_id())}\n"
            f"❌ 此指令仅限本群管理员使用\n\n"
            f"💡 请联系群管理员或使用 /gm admin add 添加管理员"
        )

    @staticmethod
    def build_rules_list(rules: List[Dict]) -> str:
        if not rules:
            return MessageBuilder.warning("当前群没有任何规则")

        message_parts = ["群规则："]
        for rule in rules:
            message_parts.append(f"\n{rule['content']}")

        return "".join(message_parts)

    @staticmethod
    def build_whitelist_list(whitelist: List[str]) -> str:
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
    def build_admin_list(admins: List[str]) -> str:
        """构建管理员列表消息"""
        if not admins:
            return MessageBuilder.warning(
                "当前群未配置管理员\n\n"
                "💡 未配置管理员时，所有用户都可管理\n"
                "使用 /gm admin add [用户ID] 添加管理员"
            )

        message_parts = [
            "📋 当前群管理员列表\n",
            "=" * 40 + "\n"
        ]
        for idx, user_id in enumerate(admins, 1):
            message_parts.append(f"{idx}. {user_id}\n")
        message_parts.append(f"\n📊 总计: {len(admins)} 人")

        return "".join(message_parts)

    @staticmethod
    def build_test_result(
        test_text: str,
        matched: bool,
        matched_rules: List[Dict]
    ) -> str:
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
        return """🤖 GroupManager 群管理器帮助

📌 功能介绍
本插件支持通过关键词、正则表达式、白名单和黑名单验证加群申请。
每个群独立管理：独立的规则、管理员、白名单和黑名单。

💻 指令列表

🔧 /gm add [关键词|正则表达式]
   添加关键词或正则表达式规则（首次使用自动启用本群）
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

👑 /gm admin add [用户ID]
   添加本群管理员
   示例: /gm admin add 123456

👑 /gm admin remove [用户ID]
   移除本群管理员
   示例: /gm admin remove 123456

👑 /gm admin list
   查看本群管理员列表

✅ /gm enable
   启用本群的群管理功能

🚫 /gm disable
   禁用本群的群管理功能

⚪ /gm whitelist add [用户ID]
   添加用户到白名单

⚫ /gm blacklist add [用户ID]
   添加用户到黑名单

⚪ /gm whitelist remove [用户ID]
   从白名单移除用户

⚫ /gm blacklist remove [用户ID]
   从黑名单移除用户

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
- 每个群独立管理管理员、规则和名单
- 未配置管理员时，所有用户都可管理
- /gm add 首次使用会自动启用本群

📚 正则表达式示例
- 手机号: /\\d{11}/
- QQ号: /[1-9][0-9]{4,}/
- 邮箱: /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}/
- 学号: /\\d{8,12}/
- 身份证: /\\d{17}[\\dXx]/

⚙️ 开发者: Kush-ShuL
🔗 项目: https://github.com/Kush-ShuL/GroupManager"""
