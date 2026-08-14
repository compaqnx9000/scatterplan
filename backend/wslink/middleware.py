from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.db import close_old_connections
from channels.db import database_sync_to_async

User = get_user_model()


class JwtAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = scope["query_string"].decode()
        params = parse_qs(query_string)
        token = params.get("token", [None])[0]

        scope["user"] = AnonymousUser()

        if token:
            try:
                access_token = AccessToken(token)
                user_id = access_token["user_id"]
                # 使用 sync_to_async 包装数据库查询操作
                user = await database_sync_to_async(User.objects.get)(id=user_id)
                # print(f"认证用户: {user}")
                scope["user"] = user
            except Exception as e:
                print(f"认证失败: {e}")

        close_old_connections()
        return await super().__call__(scope, receive, send)
