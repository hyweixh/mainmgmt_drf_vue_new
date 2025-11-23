from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import holidayfree_update

# app_name = 'holidayfree'

router = DefaultRouter(trailing_slash=False)
router.register("holidayfree", views.HolidayfreeViewSet, basename='holidayfree')

# 假设您希望所有URL都在/api/下
urlpatterns = [
    path('', include(router.urls)),  # 将router生成的URL放在根路径下（相对于/holidayfree/）
    path('update', views.holidayfree_update, name='holidayfree_update'),
]
