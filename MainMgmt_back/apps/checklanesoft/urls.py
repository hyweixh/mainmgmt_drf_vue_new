from django.urls import path,include
from . import views
from rest_framework.routers import DefaultRouter
# from .views import get_Checklanesoft_info, UpdateAllConfirmLaneSoftView,checklanesoft_download


# app_name = 'checklanesoft'  # 建议移除，避免命名空间干扰

# 创建路由器但不直接 include 到 urlpatterns
router = DefaultRouter(trailing_slash=False)
router.register(r'checklanesoft', views.ChecklanesoftViewSet, basename='checklanesoft')

# 明确定义所有路由
urlpatterns = [
    # API 视图集路由（如果需要）
    path('', include(router.urls)),

    # 自定义功能路由
    path('getchecklanesoft', views.get_Checklanesoft_info, name='getchecklanesoft'),
    path('getquerycondition', views.get_query_condition, name='getquerycondition'),
    path('confirm', views.UpdateAllConfirmLaneSoftView.as_view(), name='confirm'),
    path('download', views.checklanesoft_download, name='download'),
]