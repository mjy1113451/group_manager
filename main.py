# 文件路径：data/plugins/your_plugin_name/main.py
# 请根据实际插件目录修改 your_plugin_name

from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from typing import List, Optional
import asyncio

@register("group_join_approver", "YourName", "自动审核与通知群申请插件", "1.0.0")
class GroupJoinApprover(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self._metadata = self._get_metadata()
        self._keywords: List[str] = self._load_keywords()
        self._admin_user_ids: List[str] = self._load_admin_users()
        self._pending_requests = {}  # 用于缓存未处理的申请信息

    def _get_metadata(self):
        """从metadata.yaml加载插件元数据"""
        # 这里简化处理，实际应从metadata.yaml读取
        # metadata.yaml文件应位于插件根目录
        return {
            "name": "group_join_approver",
            "author": "YourName",
            "description": "自动审核与通知群申请插件",
            "version": "1.0.0"
        }

    def _load_keywords(self) -> List[str]:
        """加载审核关键词列表"""
        # 在实际插件中，应从配置文件或数据库加载
        # 这里使用示例关键词
        return ["面试", "求职", "项目合作", "技术交流"]

    def _load_admin_users(self) -> List[str]:
        """加载管理员用户ID列表"""
        # 在实际插件中，应从配置文件或数据库加载
        # 这里使用示例用户ID
        return ["12345678", "87654321"]  # 替换为实际的管理员用户ID

    @filter.event_message_type(filter.EventMessageType.GROUP_REQUEST)
    async def on_group_request(self, event: AstrMessageEvent):
        """
        监听群申请事件
        EventMessageType.GROUP_REQUEST 为群申请事件类型
        """
        request_info = self._extract_request_info(event)
        if not request_info:
            return

        request_id = request_info.get("request_id", "")
        group_id = request_info.get("group_id", "")
        user_id = request_info.get("user_id", "")
        user_name = request_info.get("user_name", "未知用户")
        request_reason = request_info.get("reason", "")

        # 缓存申请信息以便后续处理
        self._pending_requests[request_id] = request_info

        # 检查申请理由是否包含关键词
        matched_keyword = self._check_keywords(request_reason)

        if matched_keyword:
            # 匹配关键词，自动同意申请
            success = await self._approve_request(group_id, user_id, request_id)
            if success:
                log_message = f"已自动同意 {user_name}({user_id}) 的入群申请。匹配关键词: {matched_keyword}"
                self._log_action(log_message, event)
                # 可选：向申请人发送成功通知
                await self._notify_applicant(user_id, "您的入群申请已自动通过审核。", event)
        else:
            # 未匹配关键词，通知管理员审核
            await self._notify_admins(request_info, event)
            log_message = f"已将 {user_name}({user_id}) 的入群申请转交人工审核。申请理由: {request_reason}"
            self._log_action(log_message, event)

    def _extract_request_info(self, event: AstrMessageEvent) -> dict:
        """
        从事件对象中提取申请信息
        注意：不同平台适配器的具体字段可能不同，需根据实际情况调整
        """
        try:
            message_obj = event.message_obj
            raw_message = getattr(message_obj, 'raw_message', {})

            # 根据平台适配器类型提取不同字段
            # 这里以OneBot v11为例，其他平台需调整
            if hasattr(raw_message, 'request_type'):
                # OneBot v11的群申请格式
                return {
                    "request_id": raw_message.get("request_id", ""),
                    "group_id": raw_message.get("group_id", ""),
                    "user_id": raw_message.get("user_id", ""),
                    "user_name": raw_message.get("user_name", ""),
                    "reason": raw_message.get("comment", "")
                }
            else:
                # 通用格式尝试
                return {
                    "request_id": getattr(raw_message, 'request_id', ''),
                    "group_id": getattr(raw_message, 'group_id', ''),
                    "user_id": getattr(raw_message, 'user_id', ''),
                    "user_name": event.get_sender_name(),
                    "reason": event.message_str
                }
        except Exception as e:
            self._log_action(f"提取申请信息失败: {str(e)}", event)
            return {}

    def _check_keywords(self, text: str) -> Optional[str]:
        """检查文本是否包含关键词，返回匹配到的关键词"""
        if not text:
            return None

        text_lower = text.lower()
        for keyword in self._keywords:
            if keyword.lower() in text_lower:
                return keyword
        return None

    async def _approve_request(self, group_id: str, user_id: str, request_id: str) -> bool:
        """
        同意群申请
        注意：此功能需要平台适配器支持群管理操作
        """
        try:
            # 调用平台适配器的同意方法
            # 具体方法名可能因平台而异，以下为示例
            if hasattr(self.context, 'approve_group_request'):
                result = await self.context.approve_group_request(
                    group_id=group_id,
                    user_id=user_id,
                    request_id=request_id
                )
                return True
            else:
                self._log_action("当前平台适配器不支持同意群申请", None)
                return False
        except Exception as e:
            self._log_action(f"同意申请失败: {str(e)}", None)
            return False

    async def _notify_applicant(self, user_id: str, message: str, event: AstrMessageEvent):
        """向申请人发送通知"""
        try:
            # 构造私聊消息
            await event.send(
                target_id=user_id,
                message_type="private",
                message=message
            )
        except Exception as e:
            self._log_action(f"通知申请人失败: {str(e)}", event)

    async def _notify_admins(self, request_info: dict, event: AstrMessageEvent):
        """通知管理员有新的申请需要审核"""
        if not self._admin_user_ids:
            self._log_action("未配置管理员用户ID，无法通知", event)
            return

        user_name = request_info.get("user_name", "未知用户")
        user_id = request_info.get("user_id", "")
        group_id = request_info.get("group_id", "")
        reason = request_info.get("reason", "无申请理由")
        request_id = request_info.get("request_id", "")

        # 构造通知消息
        notification_message = (
            f"🔔 **新入群申请需审核**\n\n"
            f"**申请人**: {user_name} (ID: {user_id})\n"
            f"**申请群组**: {group_id}\n"
            f"**申请理由**: {reason}\n"
            f"**申请ID**: {request_id}\n\n"
            f"请及时审核处理。"
        )

        # 逐个通知管理员
        for admin_id in self._admin_user_ids:
            try:
                await event.send(
                    target_id=admin_id,
                    message_type="private",
                    message=notification_message
                )
                # 避免消息发送过快
                await asyncio.sleep(0.5)
            except Exception as e:
                self._log_action(f"通知管理员 {admin_id} 失败: {str(e)}", event)

    def _log_action(self, message: str, event: Optional[AstrMessageEvent] = None):
        """记录操作日志"""
        timestamp = int(asyncio.get_event_loop().time())
        log_entry = f"[{timestamp}] {message}"
        # 在实际插件中，应将日志写入文件或数据库
        # 这里仅作为示例
        # 注意：根据用户要求，不使用print

    # 可选：提供管理员指令手动审核
    @filter.command("approve")
    @filter.permission_type(filter.PermissionType.ADMIN)
    async def manual_approve(self, event: AstrMessageEvent, request_id: str):
        """管理员手动同意申请"""
        request_info = self._pending_requests.get(request_id)
        if not request_info:
            yield event.plain_result(f"未找到申请ID: {request_id}")
            return

        group_id = request_info.get("group_id", "")
        user_id = request_info.get("user_id", "")

        success = await self._approve_request(group_id, user_id, request_id)
        if success:
            del self._pending_requests[request_id]
            yield event.plain_result(f"已手动同意申请 {request_id}")
        else:
            yield event.plain_result(f"同意申请 {request_id} 失败")

    @filter.command("reject")
    @filter.permission_type(filter.PermissionType.ADMIN)
    async def manual_reject(self, event: AstrMessageEvent, request_id: str):
        """管理员手动拒绝申请"""
        request_info = self._pending_requests.get(request_id)
        if not request_info:
            yield event.plain_result(f"未找到申请ID: {request_id}")
            return

        # 这里需要实现拒绝逻辑，具体方法因平台而异
        try:
            # 示例：调用平台适配器的拒绝方法
            if hasattr(self.context, 'reject_group_request'):
                await self.context.reject_group_request(
                    group_id=request_info.get("group_id", ""),
                    user_id=request_info.get("user_id", ""),
                    request_id=request_id
                )
            del self._pending_requests[request_id]
            yield event.plain_result(f"已手动拒绝申请 {request_id}")
        except Exception as e:
            yield event.plain_result(f"拒绝申请失败: {str(e)}")
