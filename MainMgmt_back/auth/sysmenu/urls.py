from django.urls import path
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter(trailing_slash=False)
router.register(r'menus', MenuViewSet, basename='menu')

app_name = 'menu'
urlpatterns = [

]
urlpatterns += router.urls