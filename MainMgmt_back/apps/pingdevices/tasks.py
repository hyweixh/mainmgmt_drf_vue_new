# apps/pingdevices/tasks.py
# 优化 Celery 任务（使用多线程）
from celery import shared_task
from ping3 import ping
from django.core.cache import cache
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def batch_ping_ips(self, ip_list):
    """批量Ping IP地址（并发版）"""
    total = len(ip_list)
    results = {'success': [], 'timeout': [], 'error': []}
    statistics = {'success': 0, 'failed': 0, 'total': total, 'success_rate': 0}

    # 获取设备详情
    cache_key = f"ping_devices_{self.request.id}"
    devices = cache.get(cache_key, [])

    # ✅ 关键调试日志
    logger.info(f"【任务 {self.request.id}】从缓存获取 {len(devices)} 条设备信息")
    if devices:
        logger.info(f"【任务 {self.request.id}】设备样例: {devices[0]}")
    else:
        logger.warning(f"【任务 {self.request.id}】⚠️ 缓存中无设备信息！")

    device_map = {d['deviceip']: d for d in devices} if devices else {}

    # 使用线程锁保护共享数据
    lock = threading.Lock()

    def ping_single(ip):
        """单个ping任务"""
        try:
            response_time = ping(ip, timeout=1, unit='ms')  # 1秒超时

            device_info = device_map.get(ip, {})
            base_data = {
                'deviceip': ip,
                'position': device_info.get('position', ''),
                'devicename': device_info.get('devicename', '未知设备'),
                'devicetype': device_info.get('devicetype'),
            }

            if response_time is not None:
                with lock:
                    results['success'].append({
                        **base_data,
                        'response_time': round(response_time, 2)
                    })
                    statistics['success'] += 1
                return 'success'
            else:
                with lock:
                    results['timeout'].append({
                        **base_data,
                        'error_message': '设备无响应（超时）'
                    })
                    statistics['failed'] += 1
                return 'timeout'

        except Exception as e:
            device_info = device_map.get(ip, {})
            with lock:
                results['error'].append({
                    'deviceip': ip,
                    'position': device_info.get('position', ''),
                    'devicename': device_info.get('devicename', '未知设备'),
                    'devicetype': device_info.get('devicetype'),
                    'error_message': str(e)
                })
                statistics['failed'] += 1
            return 'error'

    # 使用线程池并发执行（最大50线程）
    with ThreadPoolExecutor(max_workers=50) as executor:
        # 提交所有任务
        future_to_ip = {executor.submit(ping_single, ip): ip for ip in ip_list}

        # 处理完成的任务
        for i, future in enumerate(as_completed(future_to_ip)):
            ip = future_to_ip[future]
            try:
                future.result()  # 获取结果（会抛出异常如果有）
            except Exception as e:
                print(f"Thread error for {ip}: {e}")

            # 每完成10个设备更新一次进度
            if i % 10 == 0 or i == total - 1:
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'progress': {
                            'completed': i + 1,
                            'total': total,
                            'percentage': round(((i + 1) / total) * 100, 2)
                        },
                        'statistics': statistics,
                        'results': results
                    }
                )

    # 计算成功率
    if total > 0:
        statistics['success_rate'] = round((statistics['success'] / total) * 100, 2)

    return {
        'state': 'SUCCESS',
        'is_completed': True,
        'statistics': statistics,
        'results': results
    }