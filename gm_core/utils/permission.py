"""
权限检查模块

负责检查用户权限，支持每个群独立的管理员列表。
"""

from astrbot.api.event import AstrMessageEvent
from ..core import Storage


async def is_admin(event: AstrMessageEvent, storage: Storage) -> bool:
    """
    检查用户是否为当前群的管理员

    优先检查群独立管理员列表。
    如果群未配置管理员列表，则所有用户都视为管理员。

    Args:
        event: 消息事件
        storage: 存储对象

    Returns:
        如果是管理员返回 True，否则返回 False
    """
    group_id = event.message_obj.group_id
    user_id = event.get_sender_id()

    if group_id:
        group_admins = await storage.get_group_admins(group_id)
        if group_admins:
            return user_id in group_admins
        # 未配置群管理员列表时，所有用户都视为管理员
        return True

    return False
