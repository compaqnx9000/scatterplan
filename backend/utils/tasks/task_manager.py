import concurrent.futures
import threading
import os
import django

def _worker_init():
    """工作进程初始化，确保 Django 环境在加载 tasks 前已经挂载"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scattering.settings')
    django.setup()

class TaskManager:
    """
    轻量级的多进程任务管理器，用来替换 Celery。
    使用 ProcessPoolExecutor 隔离计算密集型任务（如 GDAL 操作），防止阻塞 Django Channels 的主事件循环及其 ASGI 线程。
    单例模式。
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(TaskManager, cls).__new__(cls)
                    # 延迟初始化进程池，防止 Windows 上的导入自动触发 ProcessPoolExecutor 进而产生无限递归 (fork bomb)
                    cls._instance.executor = None
        return cls._instance

    def submit(self, fn, *args, **kwargs):
        """
        提交一个后台计算任务
        """
        if self.executor is None:
            with self._lock:
                if self.executor is None:
                    self.executor = concurrent.futures.ProcessPoolExecutor(
                        max_workers=4,
                        initializer=_worker_init
                    )

        future = self.executor.submit(fn, *args, **kwargs)
        
        # 可以在这里添加一个回调处理函数来捕获进程池崩溃等极端错误
        def check_exception(f):
            try:
                f.result()
            except Exception as e:
                print(f"[TaskManager] 后台任务执行异常: {e}")
                import traceback
                traceback.print_exc()

        future.add_done_callback(check_exception)
        return future

# 导出一个全局单例供 consumers 导入使用
task_manager = TaskManager()
