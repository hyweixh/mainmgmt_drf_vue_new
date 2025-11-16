from rest_framework import status
from rest_framework.response import Response
from auth.sysuser.serializers import *
from rest_framework.views import APIView
from django.db import transaction
from auth.sysmenu.serializers import *
from auth.rbac.permissions.drf import CustomPermissionMixin
from rest_framework import viewsets

class SysRoleViewSet(viewsets.ModelViewSet):
    """
    角色的增删改查视图集
    """
    queryset = SysRole.objects.all()  # 查询所有角色
    serializer_class = SysRoleSerializer  # 使用 SysRoleSerializer 序列化器
    permission_classes = [CustomPermissionMixin]
    permission_code_map = {
        'create': 'role:add',
        'update': 'role:edit',
        'destroy': 'role:delete',
        'list': 'role:list',
    }

    def create(self, request, *args, **kwargs):
        """
        重写 create 方法，处理角色创建
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """
        重写 update 方法，处理角色更新
        """
        partial = kwargs.pop('partial', False)  # 检查是否为部分更新
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        重写 destroy 方法，处理角色删除
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

class AssignMenuToRoleView(APIView):
    """
    视图：为角色分配菜单
    """
    permission_classes = [CustomPermissionMixin]
    permission_code_map = {
        'create': 'role:permission',
    }

    def post(self, request):
        # 获取角色ID和菜单ID列表
        role_id = request.data.get('role_id')
        menu_ids = request.data.get('menu_ids')

        # 校验角色ID是否存在
        if not role_id:
            return Response({'error': '角色ID不能为空。'}, status=status.HTTP_400_BAD_REQUEST)

        # 校验角色是否存在
        try:
            role = SysRole.objects.get(id=role_id)
        except SysRole.DoesNotExist:
            return Response({'error': '角色不存在。'}, status=status.HTTP_400_BAD_REQUEST)

        # 校验菜单是否有效
        menus = SysMenu.objects.filter(id__in=menu_ids)
        if len(menus) != len(menu_ids):
            return Response({'error': '一个或多个菜单项不存在。'}, status=status.HTTP_400_BAD_REQUEST)

        # 使用事务处理，确保数据的一致性
        with transaction.atomic():
            # 先删除该角色原有的菜单关联
            SysRoleMenu.objects.filter(role=role).delete()

            # 为角色分配新菜单
            for menu in menus:
                SysRoleMenu.objects.create(role=role, menu=menu)

        return Response({'message': '菜单已成功分配给角色。'}, status=status.HTTP_200_OK)


class RoleMenuAPIView(APIView):
    """
    获取角色对应的菜单列表，支持通过角色ID过滤
    """
    permission_classes = [CustomPermissionMixin]
    permission_code_map = {
        'list': 'role:menuList',
    }
    def get(self, request, role_id=None):
        """
        GET请求处理
        如果提供了role_id参数，返回对应角色的菜单。
        如果没有提供role_id参数，返回所有角色的菜单。
        """
        if role_id:
            try:
                # 查找对应的角色
                role = SysRole.objects.get(pk=role_id)

                # 获取该角色所关联的菜单
                role_menus = SysRoleMenu.objects.filter(role=role).values_list('menu', flat=True)
                menus = SysMenu.objects.filter(id__in=role_menus).order_by('order_num')
            except SysRole.DoesNotExist:
                return Response({'detail': 'Role not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            # 查询所有角色的菜单
            role_menus = SysRoleMenu.objects.all().values_list('menu', flat=True)
            menus = SysMenu.objects.filter(id__in=role_menus).order_by('order_num')

        # 序列化菜单数据
        serializer = SysMenuSerializer(menus, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)