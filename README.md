# ScatterPlan · 散射通信规划系统

前后端一体仓库。

## 目录

- `front/SitePlanningSystem` — Vue 3 + Element Plus + Mars3D 前端
- `backend` — Django + Celery + Redis 后端

## 前端

```bash
cd front/SitePlanningSystem
npm install
npm run dev
```

默认开发端口见 `vite.config.ts`（当前为 8086）。

## 后端

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py runserver 8888
```

Celery（Windows 建议 threads 池）：

```bash
celery -A projects worker -l info --pool=threads
```

本地需自行配置 `.env`（勿提交密钥）。
