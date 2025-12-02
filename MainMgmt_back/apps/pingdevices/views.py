# apps/pingdevices/views.py

import logging
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from celery.result import AsyncResult
from .tasks import batch_ping_ips
from .models import Pingdevices
from apps.devicemgmt.models import DeviceInfo, DeviceType
from .serializers import PingResultSerializer, DeviceInfoSerializer

logger = logging.getLogger(__name__)


# ==================== 设备列表接口 ====================
@api_view(['GET'])
def device_list(request):
    """获取设备列表（从DeviceInfo表）"""
    try:
        devices = DeviceInfo.objects.all().values('id', 'deviceip', 'position', 'devicename', 'devicetype')

        device_list = []
        for device in devices:
            devicetype_data = None
            if device['devicetype']:
                try:
                    devicetype_obj = DeviceType.objects.get(id=device['devicetype'])
                    devicetype_data = {
                        'id': devicetype_obj.id,
                        'devicetypename': devicetype_obj.devicetypename
                    }
                except DeviceType.DoesNotExist:
                    pass

            device_list.append({
                'id': device['id'],
                'deviceip': device['deviceip'],
                'position': device['position'],
                'devicename': device['devicename'],
                'devicetype': devicetype_data
            })

        logger.info(f"✅ 返回 {len(device_list)} 条设备信息")
        return Response({'items': device_list, 'total': len(device_list)})

    except Exception as e:
        logger.error(f"❌ 获取设备列表失败: {str(e)}")
        return Response({'error': str(e)}, status=500)


# ==================== 启动批量Ping任务 ====================
@api_view(['POST'])
def start_batch_ping(request):
    """启动批量Ping任务（使用缓存存储设备信息）"""
    try:
        devices = list(DeviceInfo.objects.all().values('id', 'deviceip', 'position', 'devicename', 'devicetype'))

        for device in devices:
            if device['devicetype']:
                device['devicetype'] = device['devicetype']
            else:
                device['devicetype'] = None

        task = batch_ping_ips.delay([d['deviceip'] for d in devices])

        cache_key = f"ping_devices_{task.id}"
        cache.set(cache_key, devices, 3600)

        logger.info(f"✅ 任务 {task.id} 已启动，缓存了 {len(devices)} 条设备信息")
        return Response({'task_id': task.id})

    except Exception as e:
        logger.error(f"❌ 启动批量Ping失败: {str(e)}")
        return Response({'error': str(e)}, status=500)


# ==================== 获取任务进度 ====================
@api_view(['GET'])
def get_batch_ping_progress(request, task_id):
    """获取批量Ping任务进度"""
    try:
        task = AsyncResult(task_id)

        if task.state == 'PENDING':
            return Response({'state': task.state, 'message': '任务等待中...'})

        elif task.state == 'PROGRESS':
            return Response({
                'state': task.state,
                'current': task.info.get('progress', {}).get('completed', 0),
                'total': task.info.get('progress', {}).get('total', 0),
                'deviceip': task.info.get('deviceip', ''),
                'statistics': task.info.get('statistics', {}),
                'results': task.info.get('results', {})
            })

        elif task.state in ['SUCCESS', 'FAILURE']:
            result = task.result or {}

            if task.state == 'FAILURE' and task.info:
                return Response({'state': 'FAILURE', 'error': str(task.info)})

            return Response({
                'state': task.state,
                'results': result.get('results', {}),
                'statistics': result.get('statistics', {})
            })

        else:
            return Response({'state': task.state, 'message': f'未知状态: {task.state}'})

    except Exception as e:
        logger.error(f"❌ 获取任务进度失败 {task_id}: {str(e)}")
        return Response({'error': f'获取进度失败: {str(e)}'}, status=500)


# ==================== 保存 Ping 结果 ====================
@api_view(['POST'])
def save_ping_results(request):
    """保存或更新 Ping 结果（每个IP保留最新记录）"""
    data = request.data
    results = data.get('results', [])
    task_id = data.get('task_id', '')
    print("保存的数据---", results)
    if not results:
        return Response({'error': '无数据可保存'}, status=400)

    saved_count = 0
    errors = []

    for item in results:
        try:
            with transaction.atomic():
                obj, created = Pingdevices.objects.update_or_create(
                    deviceip=item['deviceip'],
                    defaults={
                        'position': item.get('position', ''),
                        'devicename': item.get('devicename', '未知设备'),
                        'devicetype_id': item.get('devicetype'),
                        'inspectresult': item.get('inspectresult', 'error'),
                        'inspector': item.get('inspector', 'system'),
                        'inspecttime': item.get('inspecttime'),
                        'response_time': item.get('response_time'),
                        'error_desc': item.get('error_desc', ''),
                        'error_proc': item.get('error_proc', ''),
                        'task_id': task_id,
                    }
                )

                saved_count += 1
                action = "插入" if created else "更新"
                logger.info(f"【保存结果】{action}设备 {obj.deviceip} - {obj.inspectresult}")

        except Exception as e:
            error_msg = f"设备 {item.get('deviceip')} 失败: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)
            continue

    response_data = {
        'saved_count': saved_count,
        'total_attempted': len(results),
        'success': len(errors) == 0,
        'errors': errors[:5]
    }

    if errors:
        response_data['warning'] = f'部分失败: {len(errors)}/{len(results)}'

    logger.info(f"【保存结果】总计: {saved_count}/{len(results)}")
    return Response(response_data)


# ==================== 历史结果查询 ====================
class PingResultPagination(PageNumberPagination):
    """分页配置 - 返回所有记录"""
    page_size = None  # None表示禁用分页，返回全部数据
    page_size_query_param = None  # 禁止客户端通过参数修改
    max_page_size = None


# class PingResultAPIView(ListAPIView):
#     """
#     历史 Ping 结果查询接口
#     GET /api/pingdevices/results/history
#
#     支持过滤参数：
#     - ip: 按设备IP过滤
#     - status: 按检测结果过滤 (在线/离线/检查失败)，支持单个或多个值，逗号分隔
#     - days: 查询最近N天的数据（默认7天）
#     """
#     queryset = Pingdevices.objects.all().order_by('-inspecttime')
#     serializer_class = PingResultSerializer
#     pagination_class = PingResultPagination
#
#     # 中文到英文的映射
#     STATUS_CHINESE_TO_ENG = {
#         '在线': 'online',
#         '离线': 'offline',
#         '检查失败': 'error',
#         # 同时保留英文值支持
#         'online': 'online',
#         'offline': 'offline',
#         'error': 'error'
#     }
#
#     def get_queryset(self):
#         queryset = super().get_queryset()
#
#         # 按IP过滤
#         ip = self.request.query_params.get('ip')
#         if ip:
#             queryset = queryset.filter(deviceip=ip)
#
#         # ====== 按检测结果过滤（支持中文和英文） ======
#         status = self.request.query_params.get('status')
#         if status:
#             # 解析逗号分隔的多个状态
#             status_list = []
#             for s in status.split(','):
#                 s = s.strip()
#                 # 映射中文到英文，过滤非法值
#                 if s in self.STATUS_CHINESE_TO_ENG:
#                     status_list.append(self.STATUS_CHINESE_TO_ENG[s])
#
#             if status_list:
#                 queryset = queryset.filter(inspectresult__in=status_list)
#
#         # 按时间范围过滤（默认7天）
#         days = self.request.query_params.get('days', '7')
#         try:
#             days = int(days)
#             start_date = timezone.now() - timedelta(days=days)
#             queryset = queryset.filter(inspecttime__gte=start_date)
#         except (ValueError, TypeError):
#             pass
#
#         return queryset
#
#     def list(self, request, *args, **kwargs):
#         """自定义响应格式，添加统计信息"""
#         response = super().list(request, *args, **kwargs)
#
#         # 添加统计
#         queryset = self.filter_queryset(self.get_queryset())
#         total = queryset.count()
#         online = queryset.filter(inspectresult='online').count()
#         offline = queryset.filter(inspectresult='offline').count()
#         error = queryset.filter(inspectresult='error').count()
#
#         response.data['statistics'] = {
#             'total': total,
#             'online': online,
#             'offline': offline,
#             'error': error,
#             'success_rate': round(online / max(total, 1) * 100, 2)
#         }
#
#         return response
class PingResultAPIView(ListAPIView):
    """
    历史 Ping 结果查询接口
    GET /api/pingdevices/results/history
    """
    queryset = Pingdevices.objects.all().order_by('position')
    serializer_class = PingResultSerializer
    pagination_class = PingResultPagination

    def get_queryset(self):
        # ... 保持原过滤逻辑 ...
        queryset = super().get_queryset()

        # 按IP过滤
        ip = self.request.query_params.get('ip')
        if ip:
            queryset = queryset.filter(deviceip=ip)

        # 按检测结果过滤（支持多选）
        status = self.request.query_params.get('status')
        if status:
            # 解析逗号分隔的多个状态，自动过滤非法值
            status_list = [
                s.strip() for s in status.split(',')
                if s.strip() in ['online', 'offline', 'error']
            ]
            if status_list:
                queryset = queryset.filter(inspectresult__in=status_list)

        # 按时间范围过滤
        days = self.request.query_params.get('days', '7')
        try:
            days = int(days)
            start_date = timezone.now() - timedelta(days=days)
            queryset = queryset.filter(inspecttime__gte=start_date)
        except (ValueError, TypeError):
            pass

        return queryset

    def list(self, request, *args, **kwargs):
        """自定义响应格式，添加统计信息"""
        response = super().list(request, *args, **kwargs)

        # 计算统计信息
        queryset = self.filter_queryset(self.get_queryset())
        total = queryset.count()
        online = queryset.filter(inspectresult='online').count()
        offline = queryset.filter(inspectresult='offline').count()
        error = queryset.filter(inspectresult='error').count()

        statistics_data = {
            'total': total,
            'online': online,
            'offline': offline,
            'error': error,
            'success_rate': round(online / max(total, 1) * 100, 2)
        }

        # ✅ 关键修复：兼容分页禁用的情况
        if isinstance(response.data, list):
            # 禁用分页时，response.data 是列表，需要包装
            response.data = {
                'results': response.data,
                'count': len(response.data),
                'statistics': statistics_data
            }
        else:
            # 启用分页时，response.data 是字典，直接添加
            response.data['statistics'] = statistics_data

        return response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
# from .models import DeviceType

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_device_types(request):
    """
    获取所有设备类型列表
    GET /api/devicemgmt/device-types/
    """
    try:
        types = DeviceType.objects.all().values('id', 'devicetypename')
        return Response({
            'success': True,
            'data': list(types),
            'count': len(types)
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)