from datetime import datetime
import os
from django.db.models import Q
from django.utils.dateparse import parse_datetime
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from auth.permission.models import *
from auth.sysmenu.serializers import *
from auth.sysmenu.views import build_menu_tree
from auth.rbac.permissions.rbac_permission import CustomPermissionMixin
from .auth import *
from .serializers import *
from utils.page import Pagination
from rest_framework.permissions import AllowAny

class LoginView(APIView):
    """
    登录视图
    处理用户登录请求，验证身份后返回 JWT token、用户信息、角色菜单及权限列表
    支持验证码验证（如配置启用）
    """
    permission_classes = [AllowAny]  # ✅ 必须添加这行！

    def get_all_menus_for_roles(self, role_ids):
        """
        递归获取指定角色及其所有父级菜单，确保菜单树完整性

        :param role_ids: 角色ID列表
        :type role_ids: list[int]
        :return: 完整的菜单对象列表（包含所有父级菜单）
        :rtype: list[SysMenu]
        """
        # 获取角色直接关联的菜单（去重）
        menus = SysMenu.objects.filter(sysrolemenu__role__in=role_ids).distinct()

        # 初始化结果列表，直接添加已查询到的菜单
        all_menus = list(menus)

        # 遍历每个菜单，递归向上查找并添加父菜单
        # 确保前端能正确渲染树形结构
        for menu in menus:
            parent_menu_id = menu.parent_id
            # 当存在父菜单ID时持续向上追溯
            while parent_menu_id:
                try:
                    parent_menu = SysMenu.objects.get(id=parent_menu_id)
                    # 避免重复添加相同的父菜单
                    if parent_menu not in all_menus:
                        all_menus.append(parent_menu)
                    # 继续向上查找父菜单的父菜单
                    parent_menu_id = parent_menu.parent_id
                except SysMenu.DoesNotExist:
                    # 父菜单不存在时终止追溯（可能已被删除）
                    break

        return all_menus

    def get_permissions_for_roles(self, role_ids):
        """
        批量获取多个角色的所有权限码

        :param role_ids: 角色ID列表
        :type role_ids: list[int]
        :return: 权限码列表（去重）
        :rtype: list[str]
        """
        # 使用values_list获取扁平化的权限码列表，flat=True返回单个值而非元组
        permissions = SysRolePermission.objects.filter(role__id__in=role_ids) \
            .values_list('permission__code', flat=True)
        return permissions

    def post(self, request):
        """
        处理登录POST请求

        :param request: 包含username/password/captcha等登录信息
        :return: 登录成功返回token及用户信息，失败返回错误提示
        """
        # 使用LoginSerializer验证登录数据（包含用户名密码校验）
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            # 验证码验证通过后，清除缓存防止重复使用
            if settings.CAPTCHA_ENABLED:
                captcha_key = serializer.validated_data.get('captcha_key')
                if captcha_key:
                    cache.delete(f"captcha_{captcha_key}")

            # 获取验证通过的用户对象，并更新最后登录时间
            user = serializer.validated_data.get('user')
            user.last_login = datetime.now()
            user.save()

            # 生成JWT令牌
            token = generate_jwt(user)

            # 查询用户关联的所有角色ID
            role_ids = SysRole.objects.filter(sysuserrole__user=user).values_list('id', flat=True)

            # 获取角色对应的完整菜单树和权限列表
            menus = self.get_all_menus_for_roles(role_ids)
            permissions = self.get_permissions_for_roles(role_ids)

            # 将扁平菜单列表转换为树形结构（递归处理）
            menu_tree = build_menu_tree(menus)

            # 序列化菜单树供前端使用
            serializer_menu_list = SysMenuSerializer(menu_tree, many=True).data

            # 统一返回结构：token、用户信息、菜单、权限
            return Response({
                'token': token,
                'user': UserSerializer(user).data,
                'menus': serializer_menu_list,
                'permissions': list(permissions),
                'message': '登录成功',
            })

        else:
            # 提取第一个错误信息作为提示（更友好的错误展示）
            message = list(serializer.errors.values())[0][0]
            return Response({"message": message}, status=status.HTTP_400_BAD_REQUEST)


class UpdateContactInfoView(APIView):
    """
    更新用户联系方式视图
    允许用户修改自己的手机号和邮箱（部分更新）
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        处理联系方式更新请求

        :param request: 包含新的手机号(telephone)和/或邮箱(email)
        :return: 更新成功返回确认信息
        """
        # 获取当前登录用户实例
        user = request.user

        # partial=True允许只更新部分字段（灵活处理只改手机号或只改邮箱）
        serializer = UpdateContactInfoSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            # 验证通过则保存
            serializer.save()
            return Response({"message": "联系方式更新成功"}, status=status.HTTP_200_OK)

        # 验证失败返回详细错误信息
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ImageView(APIView):
    """
    用户头像上传视图
    处理头像文件上传、存储和用户信息更新
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        处理头像上传请求

        :param request: 包含avatar文件对象
        :return: 上传成功返回文件名，失败返回错误信息
        """
        # 从请求中获取头像文件
        file = request.FILES.get('avatar')
        if not file:
            return Response({'message': '未上传文件'}, status=status.HTTP_400_BAD_REQUEST)

        # 提取文件扩展名（如.jpg, .png）
        file_name = file.name
        suffix_name = file_name[file_name.rfind("."):]  # 从最后一个点开始取扩展名

        # 生成新的文件名：时间戳+扩展名（避免文件名冲突）
        new_file_name = datetime.now().strftime('%Y%m%d%H%M%S') + suffix_name

        # 构建文件存储路径：MEDIA_ROOT/userAvatar/文件名
        file_dir = os.path.join(settings.MEDIA_ROOT, 'userAvatar')
        file_path = os.path.join(file_dir, new_file_name)

        # 确保存储目录存在（不存在则自动创建）
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)

        try:
            # 分块写入文件（适合大文件上传，避免内存溢出）
            with open(file_path, 'wb') as f:
                for chunk in file.chunks():
                    f.write(chunk)

            # 更新当前用户的头像字段（只保存文件名，路径由配置决定）
            user = request.user
            user.avatar = new_file_name
            user.save()

            # 返回文件名供前端拼接完整URL
            return Response({'message': '头像上传成功', 'file_name': new_file_name}, status=status.HTTP_200_OK)

        except Exception as e:
            # 捕获文件写入或数据库更新过程中的任何异常
            return Response({'message': '上传头像失败', 'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserViewSet(viewsets.ModelViewSet):
    """
    用户管理视图集
    提供用户的增删改查操作，支持按用户名和状态过滤
    包含角色分配、头像更新等特殊逻辑
    """
    queryset = opsUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [CustomPermissionMixin]

    # 注意：此映射被注释后，CustomPermissionMixin会默认允许已登录用户访问
    # 生产环境建议明确配置权限映射
    permission_code_map = {
        'create': 'user:add',
        'update': 'user:edit',
        'destroy': 'user:delete',
        'list': 'user:list'
    }

    def get_queryset(self):
        """
        根据查询参数动态过滤用户列表
        支持按用户名（模糊匹配）和状态（精确匹配）筛选

        :return: 过滤后的用户查询集
        """
        # 从URL查询参数获取过滤条件
        username = self.request.query_params.get('username')
        status = self.request.query_params.get('status')

        # 从父类获取基础查询集
        queryset = super().get_queryset()

        # 构建Q对象实现复杂查询（支持OR和AND组合）
        q_filters = Q()

        # 用户名过滤：同时匹配username和realname字段（icontains不区分大小写）
        if username:
            q_filters &= Q(username__icontains=username) | Q(realname__icontains=username)

        # 状态过滤：精确匹配
        if status:
            q_filters &= Q(status=status)

        # 应用所有过滤条件
        return queryset.filter(q_filters)

    def create(self, request, *args, **kwargs):
        """
        重写创建用户逻辑
        包含用户创建、密码加密和角色分配

        :return: 创建后的用户信息
        """
        # 复制请求数据，避免直接修改原始数据
        data = request.data.copy()

        # 验证用户数据格式
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        # 调用create_user方法创建用户（自动处理密码加密）
        user = opsUser.objects.create_user(
            username=data['username'],
            realname=data.get('realname', ''),
            email=data.get('email'),
            password=data.get('password'),  # 会被自动加密
            telephone=data.get('telephone'),
            status=data.get('status'),
        )

        # 处理角色分配（从请求数据中获取角色ID列表）
        role_ids = data.get('roles', [])
        for role_id in role_ids:
            try:
                role = SysRole.objects.get(id=role_id)
                # 创建用户-角色关联记录
                SysUserRole.objects.create(user=user, role=role)
            except SysRole.DoesNotExist:
                # 角色不存在时返回400错误（事务性保证：用户已创建但角色分配失败）
                return Response({"detail": f"Role with ID {role_id} does not exist."},
                                status=status.HTTP_400_BAD_REQUEST)

        # 返回创建的用户完整信息
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """
        重写更新用户逻辑
        支持更新用户基本信息和重新分配角色

        :return: 更新后的用户信息
        """
        # 判断是否为部分更新（PATCH请求）
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # 验证更新数据
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # 保存用户基本信息更新
        self.perform_update(serializer)

        # 处理角色更新（如果请求中包含roles字段）
        role_ids = request.data.get('roles', None)
        if role_ids is not None:
            # 先清空现有角色（全量更新模式）
            SysUserRole.objects.filter(user=instance).delete()

            # 重新分配新角色
            for role_id in role_ids:
                try:
                    role = SysRole.objects.get(id=role_id)
                    SysUserRole.objects.create(user=instance, role=role)
                except SysRole.DoesNotExist:
                    return Response({"detail": f"Role with ID {role_id} does not exist."},
                                    status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data)

    def get_permissions(self):
        """
        动态权限控制
        头像更新仅需要登录权限，其他操作需要完整的RBAC权限
        """
        # 识别头像更新请求（仅包含avatar字段的PUT请求）
        if (self.action == 'update' and
                'avatar' in self.request.data and
                len(self.request.data) == 1):
            # 仅要求用户已登录
            return [IsAuthenticated()]

        # 其他操作使用配置的权限类（CustomPermissionMixin）
        return super().get_permissions()

    def get_serializer_class(self):
        """
        动态序列化器选择
        头像更新使用专用序列化器
        """
        # 识别头像更新操作
        if self.action == 'update' and ('avatar' in self.request.data) and len(self.request.data) == 1:
            return AvatarUpdateSerializer

        # 其他操作使用默认序列化器
        return UserSerializer

    def destroy(self, request, *args, **kwargs):
        """
        删除用户
        注意：实际环境中建议做逻辑删除而非物理删除
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class RequestLogSearchView(APIView):
    """
    请求日志查询视图
    提供模糊搜索和时间范围过滤功能
    """
    permission_classes = [CustomPermissionMixin]
    permission_code_map = {
        'list': 'requestlog:list',
    }
    pagination_class = Pagination  # 使用自定义分页器

    def get(self, request, *args, **kwargs):
        """
        处理日志查询GET请求

        :param query: 模糊搜索关键词（匹配path和permission_info）
        :param start_time: 开始时间（ISO格式）
        :param end_time: 结束时间（ISO格式）
        :return: 分页后的日志列表
        """
        # 获取查询参数
        search_query = request.GET.get('query', '')
        start_time = request.GET.get('start_time', None)
        end_time = request.GET.get('end_time', None)

        # 构建查询条件（Q对象支持复杂逻辑组合）
        filter_conditions = Q()

        # 模糊搜索：同时匹配请求路径和权限信息
        if search_query:
            filter_conditions &= (Q(path__icontains=search_query) |
                                  Q(permission_info__icontains=search_query))

        # 时间范围过滤：解析ISO格式的日期时间字符串
        if start_time:
            try:
                start_time = parse_datetime(start_time)
                filter_conditions &= Q(timestamp__gte=start_time)
            except ValueError:
                return Response({"error": "Invalid start_time format"}, status=400)

        if end_time:
            try:
                end_time = parse_datetime(end_time)
                filter_conditions &= Q(timestamp__lte=end_time)
            except ValueError:
                return Response({"error": "Invalid end_time format"}, status=400)

        # 按时间戳降序排列（最新日志在前）
        logs = RequestLog.objects.filter(filter_conditions).order_by('-timestamp')

        # 使用自定义分页器（支持page_size参数）
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(logs, request)

        if page is not None:
            # 序列化分页后的数据
            serializer = RequestLogSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        # 无分页时返回全部数据（不推荐，数据量大时性能差）
        serializer = RequestLogSerializer(logs, many=True)
        return Response(serializer.data)


class ChangePasswordView(APIView):
    """
    统一密码修改视图
    支持两种模式：
    1. 用户自修改：必须提供old_password验证身份
    2. 管理员重置：无需old_password，但需要user:resetpwd权限

    权限检查由序列化器内部的权限验证逻辑处理
    """
    # 基础权限：仅要求用户已登录
    # 具体权限（user:resetpwd）在序列化器中检查
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        处理密码修改请求

        :param username: 目标用户名（管理员重置时需要）
        :param old_password: 旧密码（用户自修改时需要）
        :param new_password: 新密码
        :return: 成功提示
        """
        # 使用统一序列化器处理所有逻辑（包含权限判断和实际改密）
        ser = UnifiedPasswordSerializer(data=request.data, context={'request': request})
        ser.is_valid(raise_exception=True)

        # save()方法执行实际的密码更新操作
        ser.save()

        return Response({'message': '密码已更新'}, status=status.HTTP_200_OK)