import json
from django.core.cache import cache

class CrossProcessTaskStore:
    """
    基于 Django FileBasedCache 的多进程共享任务存储器。
    用来替换 Redis，同时解决 ProcessPoolExecutor 带来的内存隔离问题以及 Windows multiprocessing.Manager 带来的进程复制无限递归崩溃问题。
    """
    def set_task(self, task_id, data: dict, expire_seconds=3600):
        """
        跨进程存储任务信息
        """
        cache.set(f"task:{task_id}", json.dumps(data), timeout=expire_seconds)

    def get_task(self, task_id):
        """
        跨进程获取任务信息 JSON 字符串
        """
        return cache.get(f"task:{task_id}")

# 导出一个全局单例供外部替换 redis_conn 使用
task_store = CrossProcessTaskStore()
