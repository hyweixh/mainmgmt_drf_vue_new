from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import get_gantrypsam_info, gantrypsam_download

# app_name = 'gantrypsaminfo'

router = DefaultRouter(trailing_slash=False)
router.register("gantrypsaminfo", views.GantryPsamInfoViewSet, basename='gantrypsaminfo')

urlpatterns = [
      path('', include(router.urls)),
      path('getgantrypsaminfo', get_gantrypsam_info, name='getgantrypsaminfo'),
      path('download', gantrypsam_download, name='gantrypsam_download'),


]