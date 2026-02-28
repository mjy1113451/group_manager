"""
GroupManager - 智能群管理插件

一个强大的 AstrBot 群管理插件，支持通过正则表达式、关键词、
白名单和黑名单验证加群申请。

Author: Kush-ShuL
Version: v1.0.0
License: AGPL-v3
"""

__version__ = "1.0.0"
__author__ = "Kush-ShuL"

# 核心模块
from .core.config import Config
from .core.storage import Storage
from .core.validator import Validator
from .core.validator import RuleType, ValidationResult

# 处理器模块
from .handlers.rule_handler import RuleHandler
from .handlers.whitelist_blacklist_handler import WhitelistBlacklistHandler
from .handlers.group_join_request_handler import GroupJoinRequestHandler

# 工具模块
from .utils.message_builder import MessageBuilder
from .utils.permission import is_admin
from .utils.notification_manager import NotificationManager

__all__ = [
    # 核心模块
    "Config",
    "Storage",
    "Validator",
    "RuleType",
    "ValidationResult",
    # 处理器模块
    "RuleHandler",
    "WhitelistBlacklistHandler",
    "GroupJoinRequestHandler",
    # 工具模块
    "MessageBuilder",
    "is_admin",
    "NotificationManager",
]
