from rest_framework.permissions import BasePermission
from auth.sysrole.models import SysUserRole
from auth.permission.models import SysRolePermission
from rest_framework.exceptions import *


class CustomPermissionDenied(APIException):
    """"
    自定义权限异常类
    用于在权限检查失败时抛出标准化的403错误响应
    """
    status_code = 403  # HTTP状态码：禁止访问

    def __init__(self, message):
        # ✅ 正确调用父类初始化，确保DRF能正确处理
        super().__init__(detail={"message": message})


class CustomPermissionMixin(BasePermission):
    """
    自定义权限混合类
    基于RBAC模型实现细粒度的接口权限控制
    支持配置化的权限码映射和自定义错误消息
    """

    def has_permission(self, request, view):
        """
        核心权限检查方法
        DRF会在每个请求到达视图前自动调用此方法
        返回True则允许访问，返回False或抛出异常则拒绝访问

        :param request: DRF请求对象，包含当前登录用户信息
        :param view: 当前访问的视图实例
        :return: bool 是否有权限访问
        """

        # 1. 确定当前操作类型
        # 优先获取DRF视图的action属性（如'list', 'create'等）
        # 如果不是DRF视图（如APIView），则根据HTTP方法推断操作类型
        action = getattr(view, 'action', None) or self.get_action_from_method(request.method)

        # 2. 获取视图类中定义的权限映射配置
        # permission_code_map应在视图中定义为类属性，格式如：
        # {'create': 'user:add', 'destroy': 'user:delete'}
        # 如果视图未定义该属性，则返回空字典
        permission_code_map = getattr(view, 'permission_code_map', {})

        # 3. 解析权限配置项
        # 支持两种配置方式：
        # - 字符串格式：'create': 'user:add'
        # - 字典格式：'create': {'code': 'user:add', 'message': '自定义错误信息'}
        permission_info = permission_code_map.get(action)

        if isinstance(permission_info, str):
            # 配置为字符串，直接使用作为权限码
            required_permission_code = permission_info
            # 使用默认的权限拒绝提示消息
            custom_message = "您没有执行该操作的权限"

        elif isinstance(permission_info, dict):
            # 配置为字典，支持自定义错误消息
            required_permission_code = permission_info.get('code')
            # 优先使用配置中的自定义消息，提升用户体验
            custom_message = permission_info.get('message', "您没有执行该操作的权限")
        else:

            # ✅ 生产环境安全策略：未配置 = 拒绝
            import os
            # 开发环境临时放行
            if os.getenv('DJANGO_ENV') == 'development':
                return True

            # 生产环境抛异常
            raise CustomPermissionDenied(
                message=f"操作'{action}'未配置权限码，请联系管理员"
            )


        # 4. 查询当前用户的所有角色ID
        # 通过SysUserRole关联表获取用户拥有的角色列表
        user_roles = SysUserRole.objects.filter(user=request.user).values_list('role', flat=True)
        # 返回的是QuerySet，可在数据库查询中直接使用

        # 5. 检查用户角色是否拥有所需权限
        # 通过SysRolePermission关联表查询：
        # - 角色ID在用户角色列表中
        # - 权限code匹配所需权限码
        # 使用exists()进行高效查询（仅返回True/False，不加载具体数据）
        has_permission = SysRolePermission.objects.filter(
            role__in=user_roles,
            permission__code=required_permission_code
        ).exists()

        # 6. 处理权限检查结果
        if not has_permission:
            # 无权限时抛出自定义的403异常
            # 相比返回False，抛出异常可以携带具体的错误消息
            raise CustomPermissionDenied(message=custom_message)
            # 抛出异常后，DRF会捕获并返回403响应，包含detail中的message

        # 有权限则返回True，允许访问视图
        return has_permission

    def get_action_from_method(self, method):
        """
        HTTP方法到DRF操作类型的转换映射
        用于非DRF视图（如APIView）的权限判断

        :param method: HTTP请求方法字符串，如'GET', 'POST'
        :return: 对应的DRF操作类型字符串
        """
        # 定义标准映射关系
        method_action_map = {
            'POST': 'create',     # 创建资源
            'PUT': 'update',      # 全量更新
            'PATCH': 'update',    # 部分更新（与PUT使用相同权限）
            'DELETE': 'destroy',  # 删除资源
            'GET': 'list',        # 获取列表（通常GET对应list或retrieve）
        }
        # 如果方法不在映射中，则返回小写的方法名作为备用
        return method_action_map.get(method, method.lower())