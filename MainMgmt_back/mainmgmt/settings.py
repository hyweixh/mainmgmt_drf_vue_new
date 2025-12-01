import ast
import os
import environ
from pathlib import Path

# 加载.env文件
# load_dotenv()  # 或 load_dotenv(os.path.join(BASE_DIR, '.env'))

# 验证加载
print(f"当前环境: {os.getenv('DJANGO_ENV')}")  # 应打印 "development"

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
    'django_celery_beat',   # celery_app 动态任务
    "auth.sysuser.apps.OpsauthConfig",
    "auth.sysrole.apps.SysroleConfig",
    "auth.sysmenu.apps.SysmenuConfig",
    "auth.permission.apps.PermissionConfig",
    'drf_spectacular',
    'drf_spectacular_sidecar',
    # 自己开发的app
    'apps.devicemgmt',
    'apps.checklanesoft',
    'apps.vehlossrate',
    'apps.holidayfree',
    'apps.lanepsaminfo',
    'apps.gantrypsaminfo',
    'apps.pingdevices'
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
# 3. ✅ 核心修复：暴露 Content-Disposition 头
CORS_EXPOSE_HEADERS = [
    'Content-Disposition',
    'Content-Type',
    # 如果有其他自定义头，也加在这里
]

# 数据库配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env.str('DB_NAME'),
        'USER': env.str('DB_USER'),
        'PASSWORD': env.str('DB_PASSWORD'),
        'HOST': env.str('DB_HOST'),
        'PORT': env.int('DB_PORT', default=3306),

        # 连接池优化
        'CONN_MAX_AGE': 60,  # ✅ 建议改为60秒，平衡性能与连接数

        'OPTIONS': {
            # MySQL 8.0 推荐SQL模式
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION'; SET time_zone = '+08:00'",
            # 'init_command': "SET time_zone = '+08:00'",  # 可选：设置MySQL会话时区

            # 字符集（确保表也使用utf8mb4）
            'charset': 'utf8mb4',

            # 超时设置（防止僵尸连接）
            'connect_timeout': 10,
            'read_timeout': 30,
            'write_timeout': 30,

            # 事务隔离级别（避免幻读，可选）
            'isolation_level': 'read committed',
        },
        # 连接池大小限制（Django 3.2+）
        # 'CONN_HEALTH_CHECKS': True,  # 健康检查
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
USE_TZ = False      # 使用时区
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
# DNS_REDIS_URL = env.str("DNS_REDIS_URL")    # dns-redis配置
# UPSTREAM_DNS = ast.literal_eval(os.getenv('UPSTREAM_DNS', '[]'))    # 解析上游 DNS（字符串 → Python list）
# TIMEOUT = int(os.getenv('TIMEOUT', 2))      # 超时时间（默认 2 秒）
# UDP_SIZE = int(os.getenv('UDP_SIZE', 4096)) # 最大 UDP 响应长度（默认 4096 字节）

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
# 允许前端地址访问
CORS_ALLOWED_ORIGINS = [
    'http://192.168.3.115:5173',
    'http://localhost:5173',
]
# 全局缓存配置
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': env.str('CACHE_REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
        },
        'KEY_PREFIX': 'ping',  # ✅ 改为 'ping' 或移除（使用默认）
        'VERSION': 1,
        'TIMEOUT': 3600,  # ✅ 改为 1 小时，确保任务执行期间缓存有效
    }
}
# mssql参数
MSSQL_SERVER = '10.88.188.20'
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
# 设备导出用Bearer，是否起作用
SIMPLE_JWT = {
    'AUTH_HEADER_TYPES': ('Bearer', 'JWT'),  # ✅ 同时支持两种格式
}
# ping的参数
PING_ATTEMPTS = 3
PING_TIMEOUT = 2
GANTRY_SUBNETWORK_ID = 3

# Celery配置,从.env设置
# CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
# CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'
# CELERY_TASK_TIME_LIMIT = 300

# Channels配置
# ASGI_APPLICATION = 'your_project.asgi.application'
# CHANNEL_LAYERS = {
#     'default': {
#         'BACKEND': 'channels_redis.core.RedisChannelLayer',
#         'CONFIG': {"hosts": [('127.0.0.1', 6379)]},
#     },
# }