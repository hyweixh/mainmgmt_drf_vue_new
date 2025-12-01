# routing.py
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/ping/<task_id>', consumers.PingConsumer.as_asgi()),
]