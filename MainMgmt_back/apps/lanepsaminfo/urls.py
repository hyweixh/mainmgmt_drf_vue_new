from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import PsamStatusViewSet, get_lanepsam_info, lanepsam_download

# app_name = 'lanepsaminfo'

router = DefaultRouter(trailing_slash=False)
router.register("lanepsaminfo", views.LanePsamInfoViewSet, basename='lanepsaminfo')

urlpatterns = [
      path('', include(router.urls)),
      path('psamstatus', PsamStatusViewSet.as_view(), name='psamstatus'),
      path('getlanepsaminfo', get_lanepsam_info, name='getlanepsaminfo'), # 从mssql获取数据
      # path('edit', lanepsam_edit, name='lanepsam-edit'),  # 编辑坏卡信息
      path('download', lanepsam_download, name='lanepsam-download'),    # 下载车道psam卡信息

]