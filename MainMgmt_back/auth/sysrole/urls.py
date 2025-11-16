from rest_framework.routers import DefaultRouter
from .views import *
from django.urls import path


router = DefaultRouter(trailing_slash=False)
router.register(r'roles', SysRoleViewSet)  # 注册角色视图集

app_name = 'role'

urlpatterns = [
    path('assign_menu', AssignMenuToRoleView.as_view(), name='assign_menu'),   # 分配菜单
    path('role_menus/', RoleMenuAPIView.as_view(), name='all_roles_menus'),  # 查询所有角色菜单
    path('role_menus/<int:role_id>', RoleMenuAPIView.as_view(), name='role_menus'),  # 查询指定角色菜单
]

urlpatterns += router.urls