"""
WSGI config for mainmgmt project.
"""

import os
from dotenv import load_dotenv
from django.core.wsgi import get_wsgi_application

# ✅ 加载环境变量
load_dotenv()

# ✅ 正确的设置模块路径
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mainmgmt.settings')

# ✅ 获取WSGI应用
application = get_wsgi_application()