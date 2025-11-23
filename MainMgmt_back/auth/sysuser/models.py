from django.db import models
# 导入django原生的User和User父方法模型，然后重写
from django.contrib.auth.models import User, AbstractBaseUser, PermissionsMixin, BaseUserManager

# 导入make_password，用于密码加密
from django.contrib.auth.hashers import (make_password)

# 定义员工状态类，使用 IntegerChoices 提供选择项
class UserStatus(models.IntegerChoices):
    ACTIVE = 1,         # 已经激活的
    UNACTIVE = 2,       # 没有激活
    LOCKED = 3,         # 锁定

# 自定义用户管理器
class opsUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, password, **extra_fields):
        """
        创建并保存用户的方法
        """
        user = self.model(**extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)  # 保存用户到数据库
        return user

    def create_user(self, password=None, **extra_fields):
        """
        创建普通用户
        """
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        """
        创建超级用户
        """
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault('status', UserStatus.ACTIVE)

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("超级用户必须设置is_superuser=True.")

        # 这里获取 realname，如果没有传递就设置默认值
        realname = extra_fields.pop('realname', None)
        if realname is None:
            realname = "Admin"

        return self._create_user(password, **extra_fields)


# 重写User模型
class opsUser(AbstractBaseUser, PermissionsMixin):
    """
    自定义User模型
    """
    id = models.AutoField(primary_key=True)  #主键
    username = models.CharField(max_length=100, unique=True, blank=False)
    realname = models.CharField(max_length=150,unique=False)
    email = models.EmailField(unique=True, blank=False)  # 邮箱唯一，且不能为空
    telephone = models.CharField(max_length=11, blank=True)  # 手机，可以为空
    is_active = models.BooleanField(default=True)  # 关注status即可，保留django默认的模型字段
    status = models.IntegerField(choices=UserStatus, default=UserStatus.UNACTIVE)  # 状态
    avatar = models.CharField(max_length=255, null=True, default='111.jpg', verbose_name="用户头像")
    create_time = models.DateField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    latest_token = models.CharField(max_length=255, null=True, blank=True, verbose_name="最新Token")


    objects = opsUserManager()  # 使用自定义的用户管理器

    EMAIL_FIELD = "email"

    # USERNAME_FIELD是用来做鉴权的
    # from django.contrib.auth import authenticate
    # 默认鉴权写在authenticate中，为了不重写authenticate方法，所以直接把USERNAME_FIELD的值改为邮箱

    USERNAME_FIELD = "username"
    # 指定哪些字段是必须要传的，但是不能重复包含EMAIL_FIELD和USERNAME_FIELD已经设置过的值
    REQUIRED_FIELDS = ["password"]

    class Meta:
        # db_table = "sys_user"
        ordering = ("-last_login", )   # 根据date_joined倒叙排列


class RequestLog(models.Model):
    """
    日志审计模型
    """
    timestamp = models.DateTimeField()  # 时间
    client_ip = models.GenericIPAddressField()  # 存储 IP 地址
    user_info = models.CharField(max_length=100)  # 存储用户名或“匿名用户”
    method = models.CharField(max_length=10)  # 存储请求方法，如 GET, POST
    path = models.CharField(max_length=200)  # 存储请求路径
    status_code = models.IntegerField()  # 存储响应状态码
    duration = models.DecimalField(max_digits=10, decimal_places=2)  # 存储请求耗时
    os_info = models.CharField(max_length=100)  # 存储操作系统信息
    browser_info = models.CharField(max_length=100)  # 存储浏览器信息
    permission_info = models.CharField(max_length=100, null=True, blank=True)  # 权限信息

    def __str__(self):
        return f"{self.timestamp} {self.client_ip} {self.user_info} {self.method} {self.path}"
