# 使用官方轻量级 Python 基础镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 复制整个项目，包括 venv
COPY . /app/

# 设定环境变量（关闭 Python 缓存，加快容器启动）
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 激活 venv 的路径
ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"


# 可以在 docker-compose 或 run 时挂载
# 或者直接在容器内加载：
# ENV_FILE 可以指定默认 env 文件路径
ENV ENV_FILE=/app/.env

# 如果项目有 WebSocket 技术（如 Daphne / Uvicorn），开放对应端口
EXPOSE 8888

# 启动命令
# 使用 Daphne（Django Channels）
CMD ["daphne", "-b", "0.0.0.0", "-p", "8888", "scattering.asgi:application"]

# 如果用 Uvicorn（FastAPI 或 Django ASGI）
# CMD ["uvicorn", "myproject.asgi:application", "--host", "0.0.0.0", "--port", "8000"]

