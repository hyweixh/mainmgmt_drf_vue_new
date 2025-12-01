import os
from celery import Celery
from celery.signals import after_setup_logger
import logging
import certifi

# 设置django的settings模块，celery会读取这个模块中的配置信息
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mainmgmt.settings')
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
app = Celery('mainmgmt')

# 设置时区
app.conf.timezone = 'Asia/Shanghai'

## 日志管理
@after_setup_logger.connect
def setup_loggers(logger, *args, **kwargs):
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add filehandler
    fh = logging.FileHandler('celery_app.log')
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

# 配置从settins.py中读取celery配置信息，所有Celery配置信息都要以CELERY_开头
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现任务，任务可以写在app/tasks.py中
app.autodiscover_tasks()