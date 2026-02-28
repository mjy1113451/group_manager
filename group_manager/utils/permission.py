"""
权限检查模块

负责检查用户权限。
"""

from astrbot.api.event import AstrMessageEvent
from group_manager.core import Config


def is_admin(event: AstrMessageEvent, config: Config) -> bool:
    """
    检查用户是否为管理员

    Args:
        event: 消息事件
        config: 配置对象

    Returns:
        如果是管理员返回 True，否则返回 False
    """
    return config.is_admin(event.get_sender_id())
