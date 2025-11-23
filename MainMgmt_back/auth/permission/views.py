from rest_framework import viewsets, status
from rest_framework.response import Response
from .serializers import *
from .models import SysPermission
from .serializers import SysPermissionSerializer
from auth.rbac.permissions.rbac_permission import CustomPermissionMixin
import pandas as pd
from django.http import HttpResponse
from rest_framework.views import APIView

class SysPermissionViewSet(viewsets.ModelViewSet):
    """
    权限模型的增删改查视图集（单条数据操作）
    """
    queryset = SysPermission.objects.all()  # 设置基础查询集
    serializer_class = SysPermissionSerializer  # 指定序列化器
    permission_classes = [CustomPermissionMixin]  # 指定权限类

    # 自定义权限码映射表
    permission_code_map = {
        'create': 'permission:add',
        'update': 'permission:edit',
        'destroy': 'permission:delete',
        'list': 'permission:list',
    }

    def get_queryset(self):
        # 获取查询参数中的 menu_id
        menu_id = self.request.query_params.get('menu_id', None)
        if menu_id is not None:
            # 根据 menu_id 进行过滤
            return SysPermission.objects.filter(menu_id=menu_id)
        return super().get_queryset()  # 默认返回全部权限

    # 定制的删除响应内容
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"detail": "删除成功"}, status=status.HTTP_204_NO_CONTENT)

# 导出权限
class SysPermissionExportView(APIView):
    permission_classes = [CustomPermissionMixin]
    permission_code_map = {
        'list': 'permission:export',
    }

    # 使用get方法实现导出
    def get(self, request, *args, **kwargs):

        # 获取权限数据
        permissions = SysPermission.objects.all().values(
            'id', 'name', 'code', 'menu_id', 'request_method', 'url_path', 'remark'
        )

        # 使用 pandas 创建 DataFrame
        df = pd.DataFrame(list(permissions))

        # 设置响应头信息，指定文件名和类型
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="permissions.xlsx"'

        # 将 DataFrame 内容保存到 Excel 并写入响应
        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Permissions')

        return response

class SysRolePermissionViewSet(viewsets.ModelViewSet):
    """
    角色权限关联的增删改查视图
    """
    queryset = SysRolePermission.objects.all()
    serializer_class = SysRolePermissionSerializer
    pagination_class = None  # 取消分页

    def create(self, request, *args, **kwargs):
        role_id = request.data.get('role')  # 获取角色ID
        permissions = request.data.get('permissions')  # 获取权限ID列表

        # 获取当前角色的权限
        existing_role_permissions = SysRolePermission.objects.filter(role_id=role_id).values_list('permission_id', flat=True)
        existing_permission_ids = set(existing_role_permissions)

        # 找出需要添加的新权限
        new_permissions = set(permissions)
        permissions_to_add = new_permissions - existing_permission_ids  # 新增权限
        permissions_to_remove = existing_permission_ids - new_permissions  # 需要删除的权限

        # 删除不再需要的权限
        if permissions_to_remove:
            SysRolePermission.objects.filter(role_id=role_id, permission_id__in=permissions_to_remove).delete()

        # 添加新的权限
        role_permissions = [SysRolePermission(role_id=role_id, permission_id=perm_id) for perm_id in permissions_to_add]
        SysRolePermission.objects.bulk_create(role_permissions)

        return Response({"detail": "权限成功分配"}, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        queryset = super().get_queryset()
        role_id = self.request.query_params.get('role_id')  # 从查询参数中获取角色ID

        if role_id is not None:
            queryset = queryset.filter(role_id=role_id)  # 根据角色ID过滤查询集

        return queryset
