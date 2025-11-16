"""
中间件功能说明：
1. 登录检查中间件：验证用户登录状态，处理JWT令牌验证
2. 日志记录中间件：记录请求详细信息，用于审计和监控
"""
# 导入Django及DRF相关模块
from django.utils.deprecation import MiddlewareMixin  # 兼容旧版中间件的基类
from rest_framework.authentication import get_authorization_header  # 获取请求头中的认证信息
from rest_framework import exceptions  # DRF的异常类
import jwt  # JWT令牌处理库
from django.conf import settings  # 项目配置
from django.contrib.auth import get_user_model  # 获取自定义用户模型
from django.http.response import JsonResponse  # 返回JSON响应
from rest_framework.status import HTTP_403_FORBIDDEN, HTTP_401_UNAUTHORIZED  # 状态码常量
from jwt.exceptions import ExpiredSignatureError  # JWT过期异常
from django.contrib.auth.models import AnonymousUser  # 匿名用户类
from django.shortcuts import reverse  # 反向解析URL
from django.urls import resolve  # 解析URL信息


# 获取项目自定义的用户模型（在settings中配置的AUTH_USER_MODEL）
opsUser = get_user_model()


class LoginCheckMiddleware(MiddlewareMixin):
    """
    登录检查中间件：
    1. 验证请求是否携带有效的JWT令牌
    2. 对不需要登录的接口（白名单）直接放行
    3. 对需要登录的接口，验证令牌有效性并绑定用户信息到请求对象
    4. 处理令牌无效、过期、用户不存在等异常情况
    """
    # JWT令牌在请求头中的关键字（通常为"JWT"）
    keyword = "JWT"

    def __init__(self, *args, **kwargs):
        """初始化中间件，定义不需要登录即可访问的接口白名单"""
        super().__init__(*args, **kwargs)
        # 白名单：存放不需要登录就能访问的URL（通过reverse反向解析命名URL）
        self.white_list = [
            reverse('sysuser:login'),    # 登录接口
            # reverse('sysuser:slider-captcha'),  # 滑块验证码生成接口
            # reverse('sysuser:slider-verify'),  # 滑块验证码验证接口
            reverse('schema'),  # API文档接口
            reverse('redoc'),   # ReDoc文档接口
            # reverse("staff:staffActive")    # 员工激活接口（注释掉的预留接口）
        ]

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        视图处理前的钩子方法：在请求到达视图函数前执行
        参数说明：
            request: 当前请求对象
            view_func: 将要执行的视图函数
            view_args: 视图函数的位置参数
            view_kwargs: 视图函数的关键字参数
        返回值：
            None: 继续执行后续中间件和视图
            HttpResponse: 直接返回响应，不再执行视图和后续中间件
        """
        # 1. 检查请求路径是否在白名单中，或是否是媒体文件（如图片）请求
        if request.path in self.white_list or request.path.startswith(settings.MEDIA_URL):
            # 对白名单接口，设置为匿名用户（无需登录）
            request.user = AnonymousUser()
            request.auth = None
            return None  # 继续执行后续流程

        try:
            # 2. 从请求头中获取Authorization信息（格式通常为 "JWT <token>"）
            auth = get_authorization_header(request).split()  # 拆分后为 [b'JWT', b'token字符串']

            # 3. 验证JWT令牌格式是否正确
            if not auth or auth[0].lower() != self.keyword.lower().encode():
                # 没有令牌或关键字不匹配（如不是"JWT"开头）
                raise exceptions.ValidationError("请传入JWT！")

            if len(auth) != 2:
                # 令牌格式错误（如缺少令牌部分）
                raise exceptions.AuthenticationFailed('不可用的JWT请求头！')

            try:
                # 4. 提取并解码JWT令牌
                jwt_token = auth[1]  # 获取令牌部分（bytes类型）
                # 使用项目密钥解密令牌（算法与加密时一致，这里是HS256）
                jwt_info = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms='HS256')
                userid = jwt_info.get('userid')  # 从令牌中获取用户ID

                try:
                    # 5. 验证用户是否存在，并检查令牌是否为最新（防止异地登录）
                    user = opsUser.objects.get(pk=userid)  # 从数据库获取用户

                    # 对比当前令牌与用户最新令牌（如果用户在其他设备登录，旧令牌会失效）
                    if user.latest_token != jwt_token.decode():  # 注意转换为字符串比较
                        msg = '用户在其他客户端已登录'
                        return JsonResponse(data={"message": msg}, status=409)  # 409表示冲突

                    # 6. 绑定用户信息到请求对象（供后续视图使用）
                    request.user = user  # 视图中可通过request.user获取当前用户
                    request.auth = jwt_token  # 保存令牌信息

                except opsUser.DoesNotExist:
                    # 用户不存在（可能已被删除）
                    msg = '用户不存在！'
                    raise exceptions.AuthenticationFailed(msg)

            except ExpiredSignatureError:
                # 令牌过期
                msg = "Token已过期！请重新登录"
                return JsonResponse(data={"message": msg}, status=HTTP_401_UNAUTHORIZED)  # 401未授权

        except Exception as e:
            # 捕获所有异常（如令牌无效、解码失败等）
            print(e)  # 开发环境打印异常详情（生产环境可删除）
            return JsonResponse(data={"message": "请先登录！"}, status=HTTP_403_FORBIDDEN)  # 403禁止访问


# 日志记录相关模块
import logging
import time
from user_agents import parse  # 解析用户代理（浏览器/操作系统信息）
from .models import RequestLog  # 请求日志模型（需提前定义）
from auth.permission.models import SysPermission  # 系统权限模型（用于匹配操作名称）
import re  # 正则表达式（用于匹配URL路径）
from django.utils import timezone  # 时区处理


# 获取Django默认的日志记录器（在settings.LOGGING中配置）
logger = logging.getLogger('django')


class LogClientIPMiddleware:
    """
    请求日志记录中间件：
    1. 记录所有请求的详细信息（IP、用户、路径、耗时等）
    2. 解析用户代理信息（浏览器、操作系统）
    3. 匹配请求对应的权限名称（用于审计）
    4. 将日志信息存入数据库和日志文件
    """
    def __init__(self, get_response):
        """初始化中间件，接收Django的响应处理函数"""
        self.get_response = get_response  # 保存下一个中间件/视图的处理函数

    def __call__(self, request):
        """
        中间件主逻辑：在请求处理前后执行
        流程：记录请求开始时间 -> 处理请求 -> 记录请求详情 -> 返回响应
        """
        # 1. 确保请求对象有user属性（未登录时设为匿名用户）
        if not hasattr(request, 'user'):
            request.user = AnonymousUser()

        # 2. 记录请求开始时间（用于计算耗时）
        start_time = time.time()

        # 3. 提取请求基本信息
        client_ip = self.get_client_ip(request)  # 客户端IP地址
        method = request.method  # 请求方法（GET/POST等）
        path = request.path  # 请求路径（如/api/user/）

        # 4. 解析用户代理信息（浏览器和操作系统）
        user_agent_string = request.META.get('HTTP_USER_AGENT', '')  # 获取User-Agent头
        user_agent = parse(user_agent_string)  # 解析为用户代理对象
        os_info = f"{user_agent.os.family} {user_agent.os.version_string}"  # 操作系统信息
        browser_info = f"{user_agent.browser.family} {user_agent.browser.version_string}"  # 浏览器信息

        # 5. 获取当前时间（按项目时区格式化）
        current_time = timezone.localtime(timezone.now())

        # 6. 处理请求（调用下一个中间件或视图函数，获取响应）
        response = self.get_response(request)
        status_code = response.status_code  # 响应状态码（200/404等）

        # 7. 确定用户信息（登录用户显示用户名，否则为匿名）
        user_info = "匿名用户"
        if request.user and request.user.is_authenticated:
            user_info = request.user.username

        # 8. 计算请求耗时（毫秒）
        duration = (time.time() - start_time) * 1000

        # 9. 匹配请求对应的权限名称（用于标识操作含义）
        permission_info = None  # 默认为空
        sys_permissions = SysPermission.objects.all()  # 获取所有系统权限

        # 特殊路径手动匹配（部分接口可能未在权限表中定义）
        if '/home' in path:
            permission_info = '主页统计图表'
        elif '/login' in path:
            permission_info = '登录'
        elif '/api/auth/contact' in path:
            permission_info = '修改基本信息'
        elif '/api/auth/pwd' in path:
            permission_info = '修改密码'
        else:
            # 正则匹配权限表中的URL（处理带参数的路径，如/user/{id}/）
            for perm in sys_permissions:
                # 将权限表中的URL参数（如{id}）替换为正则表达式（匹配数字）
                url_pattern = re.sub(r'{\w+}', r'\\d+', perm.url_path)
                regex = re.compile(url_pattern)  # 编译正则表达式

                # 完全匹配请求路径，且请求方法一致（GET/POST等）
                if regex.fullmatch(path) and perm.request_method == method:
                    permission_info = perm.name  # 匹配到的权限名称
                    break  # 找到第一个匹配项后退出循环

        # 10. 记录日志到文件（注释掉的可选功能）
        # log_message = f"{current_time} {client_ip} {user_info} {method} {path} {status_code} {duration:.2f}ms {os_info} {browser_info} {permission_info}"
        # logger.info(log_message)

        # 11. 将日志信息存入数据库（RequestLog模型）
        RequestLog.objects.create(
            timestamp=current_time,  # 请求时间
            client_ip=client_ip,     # 客户端IP
            user_info=user_info,     # 操作用户
            method=method,           # 请求方法
            path=path,               # 请求路径
            status_code=status_code, # 响应状态码
            duration=duration,       # 耗时（毫秒）
            os_info=os_info,         # 操作系统
            browser_info=browser_info, # 浏览器
            permission_info=permission_info  # 对应的权限名称
        )

        # 12. 返回响应（继续处理后续中间件）
        return response

    def get_client_ip(self, request):
        """
        获取客户端真实IP地址：
        - 优先从X-Forwarded-For头获取（反向代理场景）
        - 否则从REMOTE_ADDR获取（直接访问场景）
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # X-Forwarded-For格式：client_ip, proxy1_ip, proxy2_ip...
            ip = x_forwarded_for.split(',')[0].strip()  # 取第一个IP
        else:
            # REMOTE_ADDR直接获取客户端IP（可能是最后一个代理的IP）
            ip = request.META.get('REMOTE_ADDR', '')
        return ip