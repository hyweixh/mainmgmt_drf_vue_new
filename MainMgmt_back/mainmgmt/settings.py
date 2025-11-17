import ast
import os
import environ
from pathlib import Path

# 读取.env文件，在服务器项目的根路径上要创建一个
env = environ.Env()
BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = 'django-insecure-x1j)veuf48jqt-szb=-4##(^tfi8etntq*70&4i!ms)brea(7k'       # 解码 JWT 密钥

# Django 已安装的应用列表
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    # 第三方应用（添加此行）
    # 'django_extensions',  # 注意是下划线，不是连字符
    'rest_framework',
    'corsheaders',  # 跨域处理
    'django_celery_beat',   # celery 动态任务
    "auth.sysuser.apps.OpsauthConfig",
    "auth.sysrole.apps.SysroleConfig",
    "auth.sysmenu.apps.SysmenuConfig",
    "auth.permission.apps.PermissionConfig",
    'drf_spectacular',
    'drf_spectacular_sidecar',
    # 自己开发的app
    'apps.devicemgmt',
    'apps.checklanesoft'
]

# 核心中间件
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # 跨域中间件，一定要放在CommonMiddleware前面
    'django.middleware.security.SecurityMiddleware',

    'django.middleware.common.CommonMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'auth.sysuser.middlewares.LoginCheckMiddleware',  # 配置拦截器中间件
    'auth.sysuser.middlewares.LogClientIPMiddleware',  # 自定义日志中间件
]
# CORS配置
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # ✅ Vite前端地址
]

# JWT认证
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',  # ✅ 确保用户已登录
    ],
}

# 数据库配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        "NAME": env.str('DB_NAME'),
        "USER": env.str('DB_USER'),
        "PASSWORD": env.str("DB_PASSWORD"),
        "HOST": env.str('DB_HOST'),
        "PORT": env.str('DB_PORT'),
        'default-character-set': 'utf8mb4'
    },
    # 'mssql': {
    #     'ENGINE': 'mssql',
    #     'NAME': 'roaddb_qxsj',
    #     'USER': 'hyits',
    #     'PASSWORD': 'hyits_93',
    #     'HOST': '127.0.0.1',
    #     'PORT': '1433',
    #     'OPTIONS': {
    #         'driver': 'ODBC Driver 18 for SQL Server',
    #         'MARS_Connection': 'True',
    #         # 'trusted_connection': 'yes',
    #     }
    # }
}

# Django REST Framework 全局配置
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'auth.sysuser.auth.UserTokenAuthentication',  # 指定默认的认证类
    ],
    'DEFAULT_PAGINATION_CLASS': 'utils.page.Pagination',    # 分页配置-全局设置
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',   # drf-spectacular
}

# ================ 杂项配置 ===================
DEBUG = True      # 开发时使用
ALLOWED_HOSTS = ['*']   # 允许任意来源访问，可配置域名或者ip ['example.com', 'www.example.com', 'api.example.com']
ROOT_URLCONF = 'mainmgmt.urls'  # 全局 URL 路由配置
WSGI_APPLICATION = 'mainmgmt.wsgi.application'  # 连接入口
LANGUAGE_CODE = 'zh-hans'  # 语言编码
USE_I18N = True     # 国际化
USE_TZ = True       # 使用时区
TIME_ZONE = 'Asia/Shanghai'     # 时区
STATIC_URL = 'static/'         # 静态文件前缀
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'    # 模型AutoField的默认类型
CORS_ALLOW_ALL_ORIGINS = True       # 允许所有跨域访问
AUTH_USER_MODEL = 'sysuser.opsUser'     # 覆盖django自带的User模型
APPEND_SLASH = False                    # 关闭重定向
MEDIA_ROOT = BASE_DIR / 'media'     # 用户上传文件保存路径
MEDIA_URL = 'media/'                # 用户上传文件的 URL 访问前缀

# ================= Celery相关配置 =================
CELERY_BROKER_URL = env.str('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = env.str('CELERY_RESULT_BACKEND')
CELERY_TASK_SERIALIZER = env.str('CELERY_TASK_SERIALIZER')
CELERY_RESULT_SERIALIZER = env.str('CELERY_RESULT_SERIALIZER')
# 重试
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_WORKER_CANCEL_LONG_RUNNING_TASKS_ON_CONNECTION_LOSS = True

# ================= Consul配置 =================
CONSUL_BASE_URL = os.getenv('CONSUL_BASE_URL')

# =================== DNS配置 ===================
DNS_REDIS_URL = env.str("DNS_REDIS_URL")    # dns-redis配置
UPSTREAM_DNS = ast.literal_eval(os.getenv('UPSTREAM_DNS', '[]'))    # 解析上游 DNS（字符串 → Python list）
TIMEOUT = int(os.getenv('TIMEOUT', 2))      # 超时时间（默认 2 秒）
UDP_SIZE = int(os.getenv('UDP_SIZE', 4096)) # 最大 UDP 响应长度（默认 4096 字节）

# =================== 验证码配置 ===================
CAPTCHA_ENABLED = env.bool('CAPTCHA_ENABLED', default=True)     # 是否开启验证码
CAPTCHA_TIMEOUT = env.int('CAPTCHA_TIMEOUT', default=60)        # 秒，缓存过期
CAPTCHA_TOLERANCE = env.int('CAPTCHA_TOLERANCE', default=6)     # 允许误差像素
CAPTCHA_WIDTH = 300                                                 # 画布宽
CAPTCHA_HEIGHT = 150                                                # 画布高
CAPTCHA_PIECE_SIZE = 60                                             # 拼图块大小（正方形边长）
CAPTCHA_BG_DIR = os.path.join(BASE_DIR, 'media', 'captcha')         # 背景图目录

# ================= api接口文档配置 =================
SPECTACULAR_SETTINGS = {
    'SERVE_PUBLIC': True,
    'SERVE_PERMISSIONS': ['rest_framework.permissions.AllowAny'],
    'SWAGGER_UI_SETTINGS': {'persistAuthorization': True},
}
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'APP_DIRS': True,
    'OPTIONS': { 'context_processors': [
        'django.template.context_processors.request',
        'django.contrib.messages.context_processors.messages',
    ]},
}]

# 全局缓存配置
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': env.str('CACHE_REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',  # 使用JSON序列化
        },
        'KEY_PREFIX': 'captcha',  # 设置为captcha前缀
        'VERSION': 1,
        'TIMEOUT': 300,  # 5分钟过期
    }
}
# mssql参数
MSSQL_SERVER = '127.0.0.1'
MSSQL_DATABASE = 'roaddb_qxsj'
MSSQL_USER = 'hyits'
MSSQL_PW = 'hyits_93'
MSSQL_PORT = '1433'

# 日志配置
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,

    # 格式化器
    "formatters": {
        "verbose": {
            "format": "%(asctime)s %(levelname)s [%(name)s] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {
            "format": "%(levelname)s [%(name)s] %(message)s",
        },
    },

    # 处理器
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": "./mainmgmt.log",
            "formatter": "verbose",
            "encoding": "utf-8",
        },
    },

    # 根 logger：捕获所有未显式配置的 logger
    "root": {
        "handlers": ["console", "file"],
        "level": "DEBUG",
    },

    # 各个子 logger 的配置
    "loggers": {
        # Django 自带的 logger
        "django": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
        # 如果你想禁用 Django 自带的 request 或 server 日志，可以这样：
        "django.server": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",      # 只记录错误级别
            "propagate": False,
        },

        # 你自己业务中用到的 alert logger
        "alert": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
