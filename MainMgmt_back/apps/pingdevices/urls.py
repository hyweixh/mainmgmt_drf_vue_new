# apps/pingdevices/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # ✅ 修改为函数视图
    path('devices/list', views.device_list, name='device_list'),

    # 其他路由保持不变
    path('ping/batch', views.start_batch_ping, name='start_batch_ping'),
    path('ping/batch/<str:task_id>', views.get_batch_ping_progress, name='get_batch_ping_progress'),
    path('save-results', views.save_ping_results, name='save_ping_results'),
    path('results/history', views.PingResultAPIView.as_view(), name='ping_results_history'),
]