from django.urls import path
from .consumers import EchoConsumer

websocket_urlpatterns = [
    path(r'wslink/', EchoConsumer.as_asgi()),
]
