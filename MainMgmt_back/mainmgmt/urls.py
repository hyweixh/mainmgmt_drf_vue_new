from django.urls import path,include,re_path
from django.views.static import serve
from mainmgmt import settings
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework.permissions import AllowAny

urlpatterns = [
    re_path('media/(?P<path>.*)', serve, {'document_root': settings.MEDIA_ROOT}, name='media'),  # 配置媒体文件的路由地址
    path('api/auth/', include('auth.sysuser.urls')), # 用户管理
    path('api/role/', include('auth.sysrole.urls')),  # 角色管理
    path('api/menu/', include('auth.sysmenu.urls')),  # 菜单管理
    path('api/permission/', include('auth.permission.urls')),  # 权限管理

    # ✅ 新增：设备管理模块（包含子网类型、设备类型、设备信息等）
    path('api/devicemgmt/', include('apps.devicemgmt.urls')),  # 设备管理
    path('api/checklanesoft/', include('apps.checklanesoft.urls')),  # 车道软件信息
    path('api/vehlossrate/', include('apps.vehlossrate.urls')),  # 车牌识别率
    path('api/holidayfree/', include('apps.holidayfree.urls')),   # 节假日免费参数
    path('api/lanepsaminfo/', include('apps.lanepsaminfo.urls')),  # 车道psam卡信息
    path('api/gantrypsaminfo/', include('apps.gantrypsaminfo.urls')),   # 门架psam卡信息

    # drf_spectacular
    path('api/schema/', SpectacularAPIView.as_view(permission_classes=[AllowAny]), name='schema'),
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema',), name='redoc'),
]
