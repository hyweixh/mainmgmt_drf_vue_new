import logging
import pyodbc
from datetime import datetime
from django.conf import settings
from django.http import JsonResponse
from rest_framework import viewsets, status
from .serializers import (GantryPsamInfoSerializer)
from .models import Gantrypsaminfo
from rest_framework.response import Response
from django.http import Http404
from utils.databaseclass import Mssql_class
from utils.export_excels import ExcelExporter
# from django.utils import timezone

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
        request_data['last_createtime'] =  datetime.now().isoformat()  # 字符串

        serializer = self.get_serializer(instance, data=request_data, partial=partial)
        serializer.is_valid(raise_exception=True)

        self.perform_update(serializer)
        return Response(serializer.data)

# 从mssql获取门架psam卡信息




# 配置日志
logger = logging.getLogger(__name__)


def get_gantrypsam_info(request):
    """从 MSSQL 获取门架 PSAM 卡信息"""

    # 1. 先验证配置是否存在
    required_settings = ['MSSQL_SERVER', 'MSSQL_DATABASE', 'MSSQL_USER', 'MSSQL_PW']
    for setting in required_settings:
        if not hasattr(settings, setting):
            error_msg = f"缺失配置项: {setting}"
            logger.error(error_msg)
            return JsonResponse({'error': error_msg}, status=500)

    db_ip = settings.MSSQL_SERVER
    db_name = settings.MSSQL_DATABASE
    db_user = settings.MSSQL_USER
    db_pw = settings.MSSQL_PW

    mssql_instance = None  # 初始化为 None

    try:
        # 2. 实例化并连接
        mssql_instance = Mssql_class(db_ip, db_name, db_user, db_pw)
        mssql_instance.connect()

        # 3. 执行查询
        query = 'EXEC wh_proc_GetGantryPsam'
        psam_info = mssql_instance.execute_query(query, ())

        if psam_info is None:
            raise Exception("查询执行失败或返回空结果")

        # 4. 处理数据（保持原有逻辑）
        current_time = datetime.now()
        processed_count = 0

        for row in psam_info:
            if row[5] is None or row[7] is None:
                continue

            data = {
                'tollid': row[0],
                'position': row[1],
                'pilenumber': row[2],
                'rsuid': row[3],
                'controlid': row[4],
                'channelid': row[5],
                'psamno': row[7],
                'statusName': row[8],
            }

            # 使用 update_or_create
            gantry_psam_info, created = Gantrypsaminfo.objects.update_or_create(
                psamno=data['psamno'],
                defaults=data
            )

            if created:
                gantry_psam_info.first_createtime = current_time
            else:
                gantry_psam_info.last_createtime = current_time

            gantry_psam_info.save()
            processed_count += 1

        logger.info(f"成功处理 {processed_count} 条 PSAM 卡记录")
        return JsonResponse({
            'message': '数据同步成功',
            'processed': processed_count
        }, status=status.HTTP_201_CREATED)

    except pyodbc.Error as e:
        # 5. 捕获数据库连接错误
        error_msg = f"数据库连接失败: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return JsonResponse({'error': error_msg}, status=500)

    except Exception as e:
        # 6. 捕获其他所有错误
        error_msg = f"同步失败: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return JsonResponse({'error': error_msg}, status=500)

    finally:
        # 7. 安全地关闭连接
        if mssql_instance and hasattr(mssql_instance, 'conn') and mssql_instance.conn:
            try:
                mssql_instance.disconnect()
            except Exception as e:
                logger.warning(f"关闭数据库连接时出错: {e}")

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