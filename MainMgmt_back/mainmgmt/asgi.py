"""
ASGI config for mainmgmt project.
"""

import os
from dotenv import load_dotenv
from django.core.asgi import get_asgi_application

# ✅ 加载环境变量（必须在设置Django设置之前）
load_dotenv()

# ✅ 正确的设置模块路径
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mainmgmt.settings')

# ✅ 获取ASGI应用
application = get_asgi_application()
