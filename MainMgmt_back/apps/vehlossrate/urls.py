from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import get_Vehlossrate_info
from .views import get_vehlossrate_imageUrl

# app_name = 'vehlossrate'

router = DefaultRouter(trailing_slash=False)
router.register("vehlossrate", views.VehlossrateViewSet, basename='vehlossrate')

# 假设您希望所有URL都在/api/下
urlpatterns = [
    path('', include(router.urls)),  # 将router生成的URL放在/api/下
    path('getvehlossrate', get_Vehlossrate_info, name='getvehlossrate'),
    path('getimageurl', get_vehlossrate_imageUrl, name='getimageurl'),
]