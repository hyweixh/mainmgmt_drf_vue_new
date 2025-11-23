import time
import datetime
from django.conf import settings
from django.http import JsonResponse
from rest_framework import viewsets, status
from .serializers import (GantryPsamInfoSerializer)
from .models import Gantrypsaminfo
from rest_framework.response import Response
from django.http import Http404
from utils.databaseclass import Mssql_class
from utils.export_excels import ExcelExporter
from django.utils import timezone

# Create your views here.
class GantryPsamInfoViewSet(viewsets.ModelViewSet):
    queryset = Gantrypsaminfo.objects.all().order_by('tollid')
    serializer_class = GantryPsamInfoSerializer

    def get_queryset(self):
        pilenumber = self.request.query_params.get('pilenumber')
        psamno = self.request.query_params.get('psamno')
        statusName = self.request.query_params.get('statusName')
        queryset = self.queryset

        if pilenumber:
            queryset = queryset.filter(pilenumber__icontains=pilenumber)
        if psamno:
            queryset = queryset.filter(psamno__icontains=psamno)
        if statusName:
            queryset = queryset.filter(statusName=statusName)

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
        # print('修改门架psam卡状态------2')
        try:
            instance = self.get_object()  # 尝试获取实例
            # print('获取到实例:', instance)  # 调试输出
        except Http404:
            # print('对象未找到------3')
            return Response({"error": "对象未找到"}, status=status.HTTP_404_NOT_FOUND)

        # 在这里修改请求数据，而不是直接修改 validated_data
        request_data = request.data.copy()
        request_data['tollid'] = '000'
        request_data['position'] = '000'
        request_data['pilenumber'] = '000'
        request_data['rsuid'] = 0
        request_data['controlid'] = 0
        request_data['channelid'] = '000'
        request_data['statusName'] = '坏卡'
        # request_data['last_createtime'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        request_data['last_createtime'] = timezone.now().isoformat()  # 字符串
        serializer = self.get_serializer(instance, data=request_data, partial=partial)
        serializer.is_valid(raise_exception=True)

        self.perform_update(serializer)
        return Response(serializer.data)

# 从mssql获取门架psam卡信息
def get_gantrypsam_info(request):
    db_ip = settings.MSSQL_SERVER
    db_name = settings.MSSQL_DATABASE
    db_user = settings.MSSQL_USER
    db_pw = settings.MSSQL_PW

    # 实例化 Mssql_class
    mssql_instance = Mssql_class(db_ip, db_name, db_user, db_pw)

    try:
        # 连接数据库
        mssql_instance.connect()
        query = 'EXEC wh_proc_GetGantryPsam'
        query_params = ()  # 不能赋予‘’
        psam_info = mssql_instance.execute_query(query, query_params)
        # print(psam_info)
        # 44001005010040', '东沙-南浦', 'K2+530', '4C2905', '1', '1', '21440007CDF4', '44010201000000511476', '正常'
        if psam_info is not None:
            # 准备要保存或更新的数据
            # current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            current_time = timezone.now()
            for row in psam_info:
                if row[5] is None:  # 跳过 psamno 为 None 的记录
                    continue

                # 准备数据字典
                data = {
                    'tollid': row[0],
                    'position': row[1],
                    'pilenumber': row[2],
                    'rsuid': row[3],
                    'controlid': row[4],
                    'channelid': row[5],
                    #'psamno': row[6],
                    'psamno': row[7],# 才是psamno
                    'statusName': row[8],
                }
                # 先尝试获取现有记录，如果存在且psamstatus_id为2，则不更新
                try:
                    # LanePsamInfo.objects.get在找到记录时会返回一个对象，而在找不到记录时会抛出异常,不会执行continue
                    existing_record = Gantrypsaminfo.objects.get(psamno=data['psamno'])
                    # 如果找到了这样的记录，继续下一个循环
                    continue
                except Gantrypsaminfo.DoesNotExist:
                    # 如果没有找到，或者找到的记录的psamstatus_id不是2，则继续执行更新或创建
                    pass
                try:
                    Gantrypsaminfo.objects.get(psamno=data['psamno'])
                    continue
                except Gantrypsaminfo.DoesNotExist:
                    pass

                # 使用 update_or_create 来更新或创建记录
                gantry_psam_info, created = Gantrypsaminfo.objects.update_or_create(
                    psamno=data['psamno'],
                    defaults={
                        'tollid': data['tollid'],
                        'position': data['position'],
                        'pilenumber': data['pilenumber'],
                        'rsuid': data['rsuid'],
                        'controlid': data['controlid'],
                        'channelid': data['channelid'],
                        'statusName': data['statusName'],
                    }
                )
                # 根据是否是新创建的记录来设置时间字段
                if created:
                    gantry_psam_info.first_createtime = current_time
                else:
                    gantry_psam_info.last_createtime = current_time

                # 保存更改
                gantry_psam_info.save()

            # 所有数据都保存或更新成功后返回响应
            return JsonResponse({'message': 'Data saved or updated successfully'}, status=201)

        else:
            # 如果 psam_info 为 None，则返回没有检索到数据的错误
            return JsonResponse({'error': 'No data retrieved'}, status=404)

    except Exception as e:
        # 捕获异常并返回错误响应
        # print(f"Error in get_lanepsam_info: {e}")
        return JsonResponse({'error': 'Failed to retrieve or update PSAM info'}, status=500)

    finally:
        # 无论是否发生异常，都断开数据库连接
        mssql_instance.disconnect()

def gantrypsam_download(request):
    queryset = Gantrypsaminfo.objects.all()  # 确保使用.all()来获取所有数据
    result = queryset.values(
        'tollid',
        'position',
        'pilenumber',
        'rsuid',
        'controlid',
        'channelid',
        'psamno',
        'statusName',
        'first_createtime',
        'last_createtime',
        'mem'
    )
    print("result---",result)
    headers = [
               {'titlename': '收费单元编号', 'col_width': 22},
               {'titlename': '门架区间', 'col_width': 20},
               {'titlename': '门架桩号', 'col_width': 10},
               {'titlename': 'RSUID', 'col_width': 8},
               {'titlename': '控制器ID', 'col_width': 8},
               {'titlename': '通道号', 'col_width': 8},
               {'titlename': 'PSAM卡号', 'col_width': 22},
               {'titlename': 'PSAM状态', 'col_width': 8},
               {'titlename': '最初获取时间', 'col_width': 22},
               {'titlename': '最后获取时间', 'col_width': 22},
               {'titlename': '备注', 'col_width': 30}
    ]
    export_filename = '门架Psam卡信息.xlsx'
    table_filename = '门架psam卡统计表'

    exporter = ExcelExporter(result, export_filename, table_filename, headers)
    response = exporter.export()

    return response