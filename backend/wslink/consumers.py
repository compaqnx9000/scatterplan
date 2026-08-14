import json
import time
import uuid

from channels.generic.websocket import AsyncWebsocketConsumer
from django_redis import get_redis_connection

from .tasks import (
    calculation_singlelink,
    calculate_coverage_common,
    calculate_clustering,
    register_running_task,
    stop_user_tasks,
    mark_task_exited,
)


class EchoConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.redis_conn = get_redis_connection("business")

        self.user_id = None
        self.user_name = None
        self.close_code = None
        self.group_name = None
        self.current_task_id = None

    async def connect(self):
        # 检查用户是否已认证
        if self.scope["user"].is_authenticated:
            self.user_id = self.scope["user"].id
            self.user_name = str(self.scope["user"])

            self.group_name = f"user_{self.user_id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
            print(f"[WebSocket] 用户 {self.user_name} 连接建立")
        else:
            # 需要认证才能连接，拒绝连接
            await self.close(code=4001)

    async def disconnect(self, close_code):
        print(f"[WebSocket] 用户 {self.user_name} 连接关闭 代码 {close_code}")
        if self.group_name:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data: str):
        try:
            data = json.loads(text_data)
            # print(f"[WebSocket] 收到 {self.user_name} 数据: {data}")

            message = data.get("message", "")
            message_type = data.get("type", "")

            if message == "ping":
                await self.send_json({'message': 'pong'})

            elif message_type == 'singlelink':
                task_id = await self._enqueue_task(
                    calculation_singlelink,
                    (self.user_id, self.channel_name, data),
                    extra={
                        "task_type": "singlelink",
                        "group_name": self.group_name,
                        "name": data.get("name", "未命名任务"),
                    },
                )
                await self.send_json({
                    "type": "task_started",
                    "task_id": task_id,
                    "task_type": "singlelink",
                    "message": "单链路计算已开始"
                })

            elif message_type == 'rectangle area coverage':
                # calculate_coverage_common.delay(self.user_id, self.group_name, data, 'rectangle')
                await self._start_coverage_task(data, 'rectangle')

            elif message_type == 'circle area coverage':
                # calculate_coverage_common.delay(self.user_id, self.group_name, data, 'circle')
                await self._start_coverage_task(data, 'circle')

            elif message_type == 'rectangle area clustering':
                # calculate_clustering.delay(self.user_id, self.group_name, data, 'rectangle')
                await self._start_clustering_task(data, 'rectangle')

            elif message_type == 'circle area clustering':
                # calculate_clustering.delay(self.user_id, self.group_name, data, 'circle')
                await self._start_clustering_task(data, 'circle')

            elif message_type == 'stop_task':
                task_id = data.get('task_id')
                await self._handle_stop_task(task_id)

            # elif message_type == 'list_active_tasks':
            #     await self._list_active_tasks()

        except json.JSONDecodeError:
            await self.send_json({'type': 'error', 'message': '无效的 JSON 格式'})
        except Exception as e:
            await self.send_json({'type': 'error', 'message': f'处理请求失败: {str(e)}'})

    async def _enqueue_task(self, task, args, extra):
        """先登记 Redis 活动任务，再投递 Celery，避免 worker 抢跑时读不到 running 状态。"""
        stop_user_tasks(self.user_id)
        task_id = str(uuid.uuid4())
        register_running_task(self.user_id, task_id, extra=extra, stop_previous=False)
        task.apply_async(args=args, task_id=task_id)
        self.current_task_id = task_id
        return task_id

    async def _start_coverage_task(self, data: dict, area_type: str):
        """启动覆盖计算任务"""
        task_id = await self._enqueue_task(
            calculate_coverage_common,
            (self.user_id, self.channel_name, data, area_type),
            extra={
                "task_type": f"coverage_{area_type}",
                "group_name": self.group_name,
                "name": data.get("name", "未命名任务"),
            },
        )

        await self.send_json({
            "type": "task_started",
            "task_id": task_id,
            "task_type": f"coverage_{area_type}",
            "message": f"{area_type}区域覆盖计算已开始",
            "name": data.get("name", "未命名任务")
        })

    async def _start_clustering_task(self, data: dict, area_type: str):
        """启动聚类计算任务"""
        task_id = await self._enqueue_task(
            calculate_clustering,
            (self.user_id, self.channel_name, data, area_type),
            extra={
                "task_type": f"clustering_{area_type}",
                "group_name": self.group_name,
                "name": data.get("name", "未命名任务"),
            },
        )

        await self.send_json({
            "type": "task_started",
            "task_id": task_id,
            "task_type": f"clustering_{area_type}",
            "message": f"{area_type}区域聚类计算已开始",
            "name": data.get("name", "未命名任务")
        })

    async def _handle_stop_task(self, task_id: str):
        """处理停止任务请求"""
        stop_user_tasks(self.user_id)
        if task_id:
            mark_task_exited(task_id)
        self.current_task_id = None

        await self.send_json({
            "type": "task_stop_requested",
            "task_id": task_id or "",
            "message": "已发送停止请求，任务将在下一个检查点停止"
        })

    # Celery 处理完任务后推送回 WebSocket
    async def send_task_message(self, task_content: dict):
        if self.close_code is not None:
            return

        # print(f"发送数据{content['message']}")
        task_id = task_content.get("task_id")
        key = f"task:{task_id}"
        msg = task_content.get("message") or {}

        active = self.redis_conn.get(f"user:{self.user_id}:active_task")
        if isinstance(active, bytes):
            active = active.decode()
        # 旧任务的进度/结果/中止提示都不能再推给前端，否则会和当前任务抢进度条
        if active and task_id and str(active) != str(task_id):
            return

        task_info = self.redis_conn.get(key)
        if not task_info:
            return

        try:
            task_data = json.loads(task_info)
        except json.JSONDecodeError:
            return

        if task_data.get("status") == "running" or msg.get("type") in ("error", "task_stop_requested"):
            await self.send_json(msg)

    async def send_json(self, content: dict):
        """包装 json 返回，支持中文"""
        # print(f"发送数据{content}")
        await self.send(text_data=json.dumps(content, ensure_ascii=False))
