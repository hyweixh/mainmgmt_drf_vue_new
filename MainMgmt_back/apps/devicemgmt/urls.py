from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DeviceInfoViewSet, SubnetTypeListView, DeviceTypeListView, DeviceinfoUploadView, \
    decrypt_password_view, DeviceinfoDownloadView


app_name = 'devicemgmt'
# router = DefaultRouter(trailing_slash=False) url以/结束
# router = DefaultRouter()
router = DefaultRouter(trailing_slash=False)
# trailing_slash=False 只影响Router自动生成的路由，
# 对手动定义的path()没有影响,为了统一，手工定义的路由尾部也不带“/”
# GET /devicemgmt/devices - 列表所有设备信息
# POST /devicemgmt/devices - 创建新的设备信息
# GET /devicemgmt/devices/{pk} - 检索单个设备信息
# PUT /devicemgmt/devices/{pk} - 更新单个设备信息
# PATCH /devicemgmt/devices/{pk} - 部分更新单个设备信息
# DELETE /devicemgmt/devices/{pk} - 删除单个设备信

# router.register(r'devicemgmt', DeviceInfoViewSet, basename='devicemgmt'),
router.register(r'devices', DeviceInfoViewSet, basename='device'),

urlpatterns = [
    path('', include(router.urls)),
    path('devices/export', DeviceinfoDownloadView.as_view(), name='device_export'),
    # http://127.0.0.1:8000/devicemgmt/subnettypes/
    path('subnet-types', SubnetTypeListView.as_view(), name='subnet-types'),
    path('device-types', DeviceTypeListView.as_view(), name='device-types'),
    path('upload', DeviceinfoUploadView.as_view(), name='devices-upload'),
    # path('download/', DeviceinfoDownloadView.as_view(), name='devices-download'),

    path('decrypt-password', decrypt_password_view, name='decrypt-password'),
]