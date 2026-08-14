from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiTypes
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser
from .serializers import (
    UserSerializer,
    LoginRequestSerializer,
    LoginResponseSerializer,
)


class IsSelfOrAdmin(permissions.BasePermission):
    """
    只有本人或管理员可以编辑 / 删除该用户
    """

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or request.user == obj


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsSelfOrAdmin]

    # 添加过滤和搜索支持
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username']  # 支持模糊搜索的字段
    ordering_fields = ['id', 'username', 'date_joined']  # 可排序字段
    ordering = ['id']  # 默认排序

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return CustomUser.objects.all()
        return CustomUser.objects.filter(id=user.id)
        # return CustomUser.objects.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not request.user.is_staff and instance != request.user:
            return Response({'message': '你无权删除其他用户'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        # 非管理员只能修改自己的信息
        if not request.user.is_staff and instance != request.user:
            return Response({'message': '你无权修改其他用户'}, status=status.HTTP_403_FORBIDDEN)

        # 阻止用户把自己禁用
        if instance == request.user:
            is_active = request.data.get('is_active')
            # 注意：请求中 is_active 可能是字符串 "false"
            if str(is_active).lower() in ['false', '0']:
                return Response({'message': '不能将自己的账号设为非激活状态'}, status=status.HTTP_400_BAD_REQUEST)

        # 如果提供了密码字段，更新密码（哈希加密）
        if 'password' in request.data:
            password = request.data['password']
            if password:
                instance.set_password(password)
                instance.save()

        return super().update(request, *args, **kwargs)

    @extend_schema(
        request=OpenApiExample(
            '批量删除用户',
            value={"ids": [1, 2, 3]},
            request_only=True
        ),
        responses={200: OpenApiTypes.OBJECT}
    )
    @action(detail=False, methods=['delete'], url_path='batch_delete')
    def batch_delete(self, request):
        if not request.user.is_staff:
            return Response({'message': '只有管理员可以批量删除用户'}, status=status.HTTP_403_FORBIDDEN)

        ids = request.data.get('ids', [])
        if not isinstance(ids, list) or not ids:
            return Response({'message': '请提供用户ID列表'}, status=status.HTTP_400_BAD_REQUEST)

        # 不能删除自己
        ids = [uid for uid in ids if uid != request.user.id]

        deleted_count, _ = CustomUser.objects.filter(id__in=ids).delete()
        return Response({'message': deleted_count}, status=status.HTTP_200_OK)


@extend_schema(
    request=LoginRequestSerializer,
    responses={
        200: LoginResponseSerializer,
        401: {"message": "用户名或密码错误"}
    },
    tags=["登录"]
)
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]  # 允许匿名用户访问

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "is_staff": user.is_staff,
            })
        return Response({"message": "用户名或密码错误"}, status=status.HTTP_401_UNAUTHORIZED)
