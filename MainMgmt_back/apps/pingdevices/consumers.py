# 七、WebSocket消费者（consumers.py）
import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache


class PingConsumer(AsyncWebsocketConsumer):
    """实时推送Ping进度"""

    async def connect(self):
        self.task_id = self.scope['url_route']['kwargs']['task_id']
        self.group_name = f"ping_task_{self.task_id}"

        # 加入组
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

        # 发送当前进度
        progress = cache.get(f"ping_task:{self.task_id}")
        if progress:
            await self.send(text_data=json.dumps(progress))

    async def disconnect(self, close_code):
        # 离开组
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def ping_progress(self, event):
        """接收组内消息并发送给客户端"""
        await self.send(text_data=json.dumps(event["progress"]))


async def notify_ping_progress(task_id, progress_data):
    """辅助函数：从任务中推送进度"""
    from channels.layers import get_channel_layer
    channel_layer = get_channel_layer()

    await channel_layer.group_send(
        f"ping_task_{task_id}",
        {
            "type": "ping_progress",
            "progress": progress_data
        }
    )