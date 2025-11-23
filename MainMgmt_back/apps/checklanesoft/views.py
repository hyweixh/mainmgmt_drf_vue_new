# import time
import datetime
from django.db.models import Q
from django.utils import timezone
from django.conf import settings
from django.http import JsonResponse
from rest_framework import viewsets, status
from .serializers import ChecklanesoftSerializer
from .models import Checklanesoft
from rest_framework.response import Response
from utils.databaseclass import Mssql_class
from rest_framework.views import APIView
from utils.export_excels import ExcelExporter
from auth.rbac.permissions.rbac_permission import CustomPermissionMixin  # ✅ 引入权限类

class ChecklanesoftViewSet(viewsets.ModelViewSet):
    queryset = Checklanesoft.objects.all().order_by('stationno', 'laneno')
    serializer_class = ChecklanesoftSerializer

    # ✅ 添加权限控制
    permission_classes = [CustomPermissionMixin]

    # ✅ 只配置list权限，其他操作（create/update/destroy）不配置
    permission_code_map = {
        'list': {'code': 'checklanesoft:view', 'message': '您没有查看车道软件参数的权限'},
        'partial_update': {'code': 'checklanesoft:edit', 'message': '您没有编辑权限'},  # 新增此行
        # 'create': {...}  # 不配置 = 默认放行（当前开发环境策略）
        # 'update': {...}  # 不配置 = 默认放行
        # 'destroy': {...} # 不配置 = 默认放行
    }

    def get_queryset(self):
        selectType = self.request.query_params.get('queryType')
        queryCondition = self.request.query_params.get('queryCondition')

        # 定义一个字典，将'selectType'映射到相应的过滤函数
        # 每个过滤函数都接受一个查询集（qs）作为参数，并返回一个新的过滤后的查询集
        filters = {
            'obublacklistversion': lambda qs: qs.filter(obublacklistversion__icontains=queryCondition),
            'spcrateversion': lambda qs: qs.filter(spcrateversion__icontains=queryCondition),
            'lanerateversion': lambda qs: qs.filter(lanerateversion__icontains=queryCondition),
            'opsver': lambda qs: qs.filter(opsver__icontains=queryCondition),
        }

        # 获取初始的queryset（这里假设self.queryset已经在类中被定义）
        queryset = self.queryset

        # 使用字典获取对应的过滤函数，并应用到queryset上
        if selectType in filters:
            queryset = filters[selectType](queryset)

        return queryset

    # 重写list方法，返回确认后的数据
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # 添加调试点
        # print(f"SQL查询: {queryset.query}")  # 查看实际SQL
        # print(f"数据总数: {queryset.count()}")  # 查看数据量
        # 查看 isconfirm 分布
        # from django.db.models import Count
        # confirm_stats = queryset.values('isconfirm').annotate(count=Count('id'))
        # print(f"isconfirm状态分布: {list(confirm_stats)}")  # 关键！看是否有0


        # 获取查询参数中的firm值，默认为None
        firm_value = request.query_params.get('firm', None)
        # print("你确认了吗？", firm_value)
        # 如果firm_value是'0'或'1'，则过滤查询集
        if firm_value in ['0', '1']:
            # 假设confirm字段是整数类型，如果是字符类型则不需要int转换
            queryset = queryset.filter(isconfirm=int(firm_value))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # 重写create方法以处理创建逻辑
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # 可以在这里添加任何额外的创建逻辑，比如设置默认字段值
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)



    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)

        # ✅ 直接调用，DRF 会自动返回 404 响应
        instance = self.get_object()

        error_desc_value = request.data.get('error_desc', None)
        error_proc_value = request.data.get('error_proc', None)

        request_data = request.data.copy()
        request_data['error_desc'] = error_desc_value
        request_data['error_proc'] = error_proc_value

        serializer = self.get_serializer(instance, data=request_data, partial=partial)
        serializer.is_valid(raise_exception=True)

        self.perform_update(serializer)
        return Response(serializer.data)



def get_query_condition(request):
    # 从查询字符串中获取 'queryType' 参数
    # http://127.0.0.1:8000/checklanesoft/getquerycondition?queryType=obublacklistversion
    filter_value = request.GET.get('queryType', None)  # 第二个参数为默认值，若未提供则返回 None
    # 若提供了过滤值，则根据此值进行过滤
    if filter_value is not None:
        # 假设 obublacklistversion 是字符串类型，并执行大小写不敏感的 LIKE 查询
        # 注意：若 obublacklistversion 为整数，应使用 exact 匹配或其他适当查询
        filtered_versions = list(Checklanesoft.objects.distinct().values_list(filter_value, flat=True))
        # 返回包含过滤后（或全部）obublacklistversion 的 JsonResponse
        return JsonResponse({'data': list(filtered_versions)}, status=200, safe=False)

# 从mssql获取车道软件信息
def get_Checklanesoft_info(request):
    db_ip = settings.MSSQL_SERVER
    db_name = settings.MSSQL_DATABASE
    db_user = settings.MSSQL_USER
    db_pw = settings.MSSQL_PW

    print(db_ip, db_name, db_user, db_pw)
    # 实例化 Mssql_class
    mssql_instance = Mssql_class(db_ip, db_name, db_user, db_pw)

    try:

        # curlogin_user获取的是admin，但是下下面的更新中用'inspector': curlogin_user会提示其值为“<UserInfo: admin>”
        curlogin_user = request.user
        query_params = ()  # 查询语句中没有占位符，不能赋予‘’
        # 连接数据库
        mssql_instance.connect()
        # 删除 Vehlossrate 表内容
        query = 'exec wh_proc_Checklanesoft'

        lanesoftpara_info = mssql_instance.execute_query(query, query_params)

        if lanesoftpara_info is not None:
            # 准备要保存或更新的数据
            # current_time与setting.py中USE_TZ设置有关，USE_TZ = True用下面复制
            # current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            current_time = timezone.now()

            for row in lanesoftpara_info:
                # 准备数据字典
                data = {
                    'stationno': row[0],
                    'tollStationname': row[1],
                    'laneno': row[2],
                    'lanetypename': row[3],
                    'obublacklistversion': row[4],
                    'spcrateversion': row[5],
                    'greenreservelistversion': row[6],
                    'bulkvehreserveversion': row[7],
                    'laneservtime': row[8],
                    'lanebeidoutime': row[9],
                    'lanerateversion': row[10],
                    'opsver': row[11],
                    # inspector 字段被设置为 request.user，这在 Django 中通常是一个用户模型实例（如 User）
                    # 在使用用户模型中的某个字符串属性，需要如此引用curlogin_user.realname，而不是整个用户对象。
                    'inspector': curlogin_user.realname,
                    'inspecttime': current_time,
                }

                lanesoftpara_info, created = Checklanesoft.objects.update_or_create(
                    stationno=data['stationno'],
                    laneno=data['laneno'],
                    isconfirm=0,
                    defaults=data
                )
            # 所有数据都保存或更新成功后返回响应
            return JsonResponse({'message': '更新车道软件参数成功！'}, status=201)

        else:
            # 如果 psam_info 为 None，则返回没有检索到数据的错误
            return JsonResponse({'error': '没有获取数据'}, status=404)

    except Exception as e:
        # 捕获异常并返回错误响应
        print(f"Error in get_Checklanesoft_info: {e}")
        return JsonResponse({'error': '更新车道软件参数失败'}, status=500)

    finally:
        # 无论是否发生异常，都断开数据库连接
        mssql_instance.disconnect()

# 检查完成后确认
class UpdateAllConfirmLaneSoftView(APIView):
    def post(self, request, *args, **kwargs):
        # 对所有记录进行更新
        current_user = request.user  # 获取当前用户
        current_time = timezone.now()

        # 更新所有记录
        Checklanesoft.objects.all().update(
            confirmer=current_user.realname if hasattr(current_user, 'realname') else 'Unknown',
            confirmdatetime=current_time,
            isconfirm=1
        )
        # 返回响应
        return Response({'status': 'All records updated successfully'}, status=status.HTTP_200_OK)


def checklanesoft_import_history(request):
    # 获取未确认记录中的最大检查时间
    max_datetime = Checklanesoft.objects.filter(isconfirm=0).aggregate(max_starttime=Max('inspecttime'))
    max_starttime = max_datetime.get('max_starttime')

    # 如果没有未确认的记录，显示提示
    if max_starttime is None:
        context = {
            'property_str': '请获取车道软件信息.',
            'ok_url': '/checklanesoft/update',
            'cancel_url': '/checklanesoft/list',
        }


        # 检查是否存在与最大检查日期相同的已确认记录
    exists = Checklanesoft.objects.filter(
        inspecttime__date=max_starttime.date(),  # 使用日期部分进行比较
        isconfirm=1
    ).exists()

    if exists:
        property_str = max_starttime.date().strftime("%Y-%m-%d") + '车道软件信息已确认！无需再次确认。'
        context = {
            'property_str': property_str,
            'ok_url': '/checklanesoft/list',
            'cancel_url': '/checklanesoft/list',
        }

    else:
        # 更新所有与最大检查日期相同的未确认记录
        objects_to_update = Checklanesoft.objects.filter(
            inspecttime__date=max_starttime.date(),
            isconfirm=0
        )
        for obj in objects_to_update:
            obj.confirmer = request.session["user_info"]['display_name']
            obj.confirmdatetime = timezone.now()  # 使用timezone.now()获取当前时间，保持为datetime对象
            obj.isconfirm = True
            obj.save()

    return JsonResponse({'message': ''}, status=201)

from django.views.decorators.http import require_http_methods
import logging
logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
def checklanesoft_download(request):
    """导出车道软件参数Excel"""
    try:
        selYM_str = request.GET.get('selYM', '2020-01')

        # 参数验证
        if not selYM_str or len(selYM_str) != 7:
            return JsonResponse({'error': '参数格式应为YYYY-MM'}, status=400)

        # ✅ 1. 查询 ORM 对象（不要 values() 或 values_list()）
        queryset = Checklanesoft.objects.filter(
            ~Q(error_desc__isnull=True) & ~Q(error_desc=''),
            isconfirm__in=[True, 1, "1", "True"],
            inspecttime__startswith=selYM_str
        )

        # logger.info(f"查询到 {queryset.count()} 条记录")

        if not queryset.exists():
            return JsonResponse({
                'error': f'{selYM_str}暂无已确认且填写故障描述的记录'
            }, status=404)

        # ✅ 2. 手动构建元组列表（核心修复）
        # 定义字段顺序（必须与 headers 一一对应）
        FIELD_ORDER = [
            'tollStationname',
            'laneno',
            'lanetypename',
            'error_desc',
            'error_proc',
            'inspector',
            'inspecttime'
        ]

        # 将 ORM 对象转换为元组列表
        export_data = []
        for obj in queryset:
            row = []
            for field_name in FIELD_ORDER:
                val = getattr(obj, field_name)

                # 处理 datetime 类型
                if isinstance(val, datetime.datetime):
                    row.append(val.strftime('%Y-%m-%d %H:%M:%S'))
                else:
                    row.append(val or '')  # 将 None 转换为空字符串

            export_data.append(tuple(row))

        # logger.info(f"第一条导出数据: {export_data[0] if export_data else '无数据'}")

        # ✅ 3. 定义表头（与 FIELD_ORDER 严格对应）
        headers = [
            {'titlename': '收费站', 'col_width': 20},
            {'titlename': '车道号', 'col_width': 16},
            {'titlename': '车道类型', 'col_width': 16},
            {'titlename': '故障描述', 'col_width': 50},
            {'titlename': '故障处理', 'col_width': 50},
            {'titlename': '巡检人员', 'col_width': 14},
            {'titlename': '巡检时间', 'col_width': 20},
        ]

        # ✅ 4. 调用 ExcelExporter（传入纯 list）
        exporter = ExcelExporter(
            export_data,  # 纯元组列表，不是 QuerySet
            f'checklanesoft_export_{selYM_str}.xlsx',
            '车道软件参数巡检表',
            headers
        )
        return exporter.export()

    except Exception as e:
        logger.error(f"导出失败: {str(e)}", exc_info=True)
        return JsonResponse({'error': f'导出失败: {str(e)}'}, status=500)
