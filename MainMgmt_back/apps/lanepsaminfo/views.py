import time
from django.conf import settings
from django.http import JsonResponse
from rest_framework.generics import ListAPIView
from rest_framework import viewsets, status
from .serializers import (LanePsamInfoSerializer, PsamStatusSerializer)
from .models import LanePsamInfo, PsamStatus
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from utils.databaseclass import Mssql_class
from utils.export_excels import ExcelExporter
from django.utils import timezone
# from openpyxl.styles import Font, Color, Alignment

class PsamStatusViewSet(ListAPIView):
    queryset = PsamStatus.objects.all().order_by('id')
    serializer_class = PsamStatusSerializer
    pagination_class = None  # 禁用分页


class LanePsamInfoViewSet(viewsets.ModelViewSet):
    queryset = LanePsamInfo.objects.all().order_by('deviceid')  # 添加排序
    serializer_class = LanePsamInfoSerializer

    # 获取车道psam卡列表（保留原来的get_queryset方法）
    def get_queryset(self):
        stationno = self.request.query_params.get('stationno')
        psamno = self.request.query_params.get('psamno')
        psamstatus_id = self.request.query_params.get('psamstatus_id')
        queryset = self.queryset

        if stationno:
            queryset = queryset.filter(stationno=stationno)
        if psamno:
            queryset = queryset.filter(psamno__icontains=psamno)
        if psamstatus_id:
            queryset = queryset.filter(psamstatus_id=psamstatus_id)

        return queryset

    # 重写create方法以处理创建逻辑
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # 可以在这里添加任何额外的创建逻辑，比如设置默认字段值
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    # 重写update方法以处理更新逻辑
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # 在这里添加更新逻辑，比如修改特定字段
        mem_value = request.data.get('mem', None)
        serializer.validated_data['deviceid'] = ''  # 示例：清空deviceid字段
        serializer.validated_data['stationno'] = 0  # 示例：设置stationno为0
        serializer.validated_data['laneno'] = 0  # 示例：设置laneno为0
        serializer.validated_data['lanecomputerip'] = '0.0.0.0'  # 示例：设置默认IP
        # serializer.validated_data['last_createtime'] = time.strftime('%Y-%m-%d %H:%M:%S',
        #                                                               time.localtime())  # 更新最后创建时间
        serializer.validated_data['last_createtime'] = timezone.now().isoformat()  # 字符串
        serializer.validated_data['psamstatus_id'] = 2  # 示例：设置psamstatus_id为2
        serializer.validated_data['mem'] = mem_value  # 设置mem字段的值

        try:
            self.perform_update(serializer)
            return Response(serializer.data)
        except Exception as e:
            # 捕获异常并返回自定义错误消息
            return Response({"detail": "修改卡状态错误! 错误详情: {}".format(str(e))},
                            status=status.HTTP_400_BAD_REQUEST)

def get_lanepsam_info(request):
    db_ip = settings.MSSQL_SERVER
    db_name = settings.MSSQL_DATABASE
    db_user = settings.MSSQL_USER
    db_pw = settings.MSSQL_PW

    # 实例化 Mssql_class
    mssql_instance = Mssql_class(db_ip, db_name, db_user, db_pw)

    try:
        # 连接数据库
        mssql_instance.connect()
        query = 'EXEC wh_proc_Getpsam'
        query_params = ()  # 不能赋予‘’
        psam_info = mssql_instance.execute_query(query,query_params)

        if psam_info is not None:
            # 准备要保存或更新的数据
            default_psam_status = get_object_or_404(PsamStatus, id=1)
            # current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            current_time = timezone.now(),
            for row in psam_info:
                if row[5] is None:  # 跳过 psamno 为 None 的记录
                    continue

                    # 准备数据字典
                data = {
                    'deviceid': row[0],
                    'stationno': row[1],
                    'laneno': row[2],
                    'lanecomputerip': row[3],
                    'terminano': row[4],
                    'psamno': row[5],
                    'psamstatus_id': default_psam_status.id,
                }
                # 先尝试获取现有记录，如果存在且psamstatus_id为2，则不更新
                try:
                    # LanePsamInfo.objects.get在找到记录时会返回一个对象，而在找不到记录时会抛出异常,不会执行continue
                    existing_record = LanePsamInfo.objects.get(psamno=data['psamno'], psamstatus_id=2)
                    # 如果找到了这样的记录，继续下一个循环
                    continue
                except LanePsamInfo.DoesNotExist:
                    # 如果没有找到，或者找到的记录的psamstatus_id不是2，则继续执行更新或创建
                    pass
                try:
                    LanePsamInfo.objects.get(stationno=data['stationno'],
                                             laneno=data['laneno'],
                                             psamno=data['psamno'])
                    continue
                except LanePsamInfo.DoesNotExist:
                    pass

                # 使用 update_or_create 来更新或创建记录
                lane_psam_info, created = LanePsamInfo.objects.update_or_create(
                    psamno=data['psamno'],  # 用于判断是否存在的唯一字段
                    defaults={
                        'deviceid': data['deviceid'],
                        'stationno': data['stationno'],
                        'laneno': data['laneno'],
                        'lanecomputerip': data['lanecomputerip'],
                        'terminano': data['terminano'],
                        'psamstatus_id': data['psamstatus_id'],
                    }
                )

                # 根据是否是新创建的记录来设置时间字段
                if created:
                    lane_psam_info.first_createtime = current_time
                else:
                    lane_psam_info.last_createtime = current_time

                # 保存更改
                lane_psam_info.save()

                # 所有数据都保存或更新成功后返回响应
            return JsonResponse({'message': 'Data saved or updated successfully'}, status=201)

        else:
            # 如果 psam_info 为 None，则返回没有检索到数据的错误
            return JsonResponse({'error': 'No data retrieved'}, status=404)

    except Exception as e:
        # 捕获异常并返回错误响应
        print(f"Error in get_lanepsam_info: {e}")
        return JsonResponse({'error': 'Failed to retrieve or update PSAM info'}, status=500)

    finally:
        # 无论是否发生异常，都断开数据库连接
        mssql_instance.disconnect()

def lanepsam_download(request):
    queryset = LanePsamInfo.objects.all().order_by('stationno', 'laneno') # 确保使用.all()来获取所有数据
    result = queryset.values(
        'deviceid',
        'stationno',
        'laneno',
        'lanecomputerip',
        'terminano',
        'psamno',
        'psamstatus__psamstatus',
        'first_createtime',
        'last_createtime',
        'mem'
    )

    headers = [
               {'titlename': '车道国标编号', 'col_width': 23},
               {'titlename': '收费站编号', 'col_width': 12},
               {'titlename': '车道编号', 'col_width': 10},
               {'titlename': '车道ip地址', 'col_width': 20},
               {'titlename': 'Psam卡终端设备编号', 'col_width': 22},
               {'titlename': 'psam卡卡号', 'col_width': 22},
               {'titlename': 'psam卡状态', 'col_width': 12},
               {'titlename': '首次记录时间', 'col_width': 22},
               {'titlename': '最后记录时间', 'col_width': 22},
               {'titlename': '备注', 'col_width': 30}
    ]
    export_filename = '车道Psam卡信息.xlsx'
    table_filename = '车道psam卡统计表'

    exporter = ExcelExporter(result, export_filename, table_filename, headers)
    response = exporter.export()

    return response
