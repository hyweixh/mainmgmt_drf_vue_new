import time
from django.conf import settings
from django.http import JsonResponse
from rest_framework import viewsets, status
from .serializers import VehlossrateSerializer
from .models import Vehlossrate
from rest_framework.response import Response
from utils.databaseclass import Mssql_class
import logging
# from django.utils import timezone  # 新增：处理时区
from datetime import datetime  # 新增
from django.db import transaction  # 新增：事务控制

logger = logging.getLogger(__name__)


class VehlossrateViewSet(viewsets.ModelViewSet):
    queryset = Vehlossrate.objects.all().order_by('tolllaneid')
    serializer_class = VehlossrateSerializer

    def get_queryset(self):
        stationno = self.request.query_params.get('stationno')
        per1 = self.request.query_params.get('per1')
        queryset = self.queryset

        if stationno:
            queryset = queryset.filter(stationno=stationno)
        if per1:
            queryset = queryset.filter(per1__lte=per1)
        return queryset


# 从mssql获取车牌识别率信息
def get_Vehlossrate_info(request):
    db_ip = settings.MSSQL_SERVER
    db_name = settings.MSSQL_DATABASE
    db_user = settings.MSSQL_USER
    db_pw = settings.MSSQL_PW

    # 获取并标准化时间参数
    starttime_str = request.GET.get('starttime', '2020-01-01 00:00:00')
    endtime_str = request.GET.get('endtime', '2024-01-01 00:00:00')
    is_NEVs = request.GET.get('is_NEVs', 'false')

    # 时间字符串转datetime对象（处理URL编码的+号）
    try:
        # 将+替换为空格
        starttime_str = starttime_str.replace('+', ' ')
        endtime_str = endtime_str.replace('+', ' ')
        start_dt = datetime.strptime(starttime_str, '%Y-%m-%d %H:%M:%S')
        end_dt = datetime.strptime(endtime_str, '%Y-%m-%d %H:%M:%S')

        # 如果USE_TZ=True，转换为时区感知对象
        if settings.USE_TZ:
            start_dt = timezone.make_aware(start_dt)
            end_dt = timezone.make_aware(end_dt)
    except ValueError as e:
        logger.error(f"时间格式错误: {e}")
        return JsonResponse({'error': '时间格式错误，应为: YYYY-MM-DD HH:MM:SS'}, status=400)

    curlogin_user = request.user

    # 实例化 Mssql_class
    mssql_instance = Mssql_class(db_ip, db_name, db_user, db_pw)

    try:
        query_params = (starttime_str, endtime_str)

        # 连接数据库
        mssql_instance.connect()

        # 修改为只删除当前时间段的数据（避免全表删除）
        # Vehlossrate.objects.all().delete()  # 危险！注释掉

        # 删除当前时间段的旧数据（更安全）
        with transaction.atomic():
            deleted_count, _ = Vehlossrate.objects.filter(
                starttime=start_dt,
                endtime=end_dt
            ).delete()
            logger.info(f"已删除 {deleted_count} 条旧记录")

        # 根据NEVs参数选择不同的存储过程
        if is_NEVs.lower() == 'true':
            query = "exec wh_proc_vehlossrate_nev @StartDate=?, @EndDate=?"
            logger.info("执行新能源车牌识别率存储过程")
        else:
            query = "exec wh_proc_vehlossrate_normal @StartDate=?, @EndDate=?"  # 确保有这个存储过程
            logger.info("执行普通车牌识别率存储过程")

        vehlossrate_info = mssql_instance.execute_query(query, query_params)

        if vehlossrate_info:
            current_time =  datetime.now()() if settings.USE_TZ else time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

            # 使用bulk_create批量插入（性能提升10倍以上）
            batch_data = []

            for row in vehlossrate_info:
                data = {
                    'tolllaneid': row[0],
                    'stationid': row[1],
                    'laneno': row[2],
                    'stationno': row[3],
                    'lanetypename': row[4],
                    'lanecomputerip': row[5],
                    'cnt': row[6],
                    'veh': row[7],
                    'scu': row[8],
                    'per': row[9],
                    'per1': row[10],
                    'per2': row[11],
                    'starttime': start_dt,
                    'endtime': end_dt,
                    'inspector': curlogin_user.realname if hasattr(curlogin_user, 'realname') else str(curlogin_user),
                    'inspecttime': current_time,
                    'isconfirm': 0,  # 明确设置
                }
                batch_data.append(Vehlossrate(**data))

            # 批量创建（自动处理唯一性）
            with transaction.atomic():
                created_objs = Vehlossrate.objects.bulk_create(
                    batch_data,
                    ignore_conflicts=True  # 忽略重复数据冲突
                )
                logger.info(f"成功插入 {len(created_objs)} 条记录")

            return JsonResponse({
                'message': '更新车牌识别率成功！',
                'count': len(created_objs)
            }, status=200)
        else:
            logger.warning("存储过程未返回数据")
            return JsonResponse({'error': 'No data retrieved'}, status=404)

    except pymssql.Error as e:
        logger.error(f"数据库错误: {e}")
        return JsonResponse({'error': '数据库查询失败'}, status=500)
    except Exception as e:
        logger.exception(f"未知错误: {e}")  # 记录完整堆栈
        return JsonResponse({'error': f'服务器错误: {str(e)}'}, status=500)
    finally:
        mssql_instance.disconnect()


# 获取车道图片连接（无需修改，但建议添加日志）
# 获取车道图片连接
def get_vehlossrate_imageUrl(request):
    logger.info(f"获取图片URL参数: {request.GET}")

    # 获取参数
    tollstationid = request.GET.get('tollstationid')
    tolllaneid = request.GET.get('tolllaneid')
    laneno = int(request.GET.get('laneno', 0))
    starttime = request.GET.get('starttime')
    endtime = request.GET.get('endtime')
    is_NEVs = request.GET.get('is_NEVs', 'false')

    print("后台获取：", tollstationid, tolllaneid, starttime, endtime, laneno, is_NEVs)

    # ==================== 简化的时间转换 ====================
    try:
        def format_datetime_for_sql(time_str):
            """将 ISO 8601 格式转换为 SQL Server 格式"""
            if not time_str:
                raise ValueError("时间参数不能为空")
            # 直接解析 ISO 8601 格式并转换
            dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d %H:%M:%S')

        starttime = format_datetime_for_sql(starttime)
        endtime = format_datetime_for_sql(endtime)
        logger.info(f"转换后的时间 - starttime: {starttime}, endtime: {endtime}")

    except (ValueError, TypeError) as e:
        logger.error(f"时间格式错误: {e}")
        return JsonResponse(
            {'error': '时间格式错误，支持 ISO 8601 格式'},
            status=400
        )
    # =================================================================

    # 数据库连接配置
    db_ip = settings.MSSQL_SERVER
    db_name = settings.MSSQL_DATABASE
    db_user = settings.MSSQL_USER
    db_pw = settings.MSSQL_PW

    # 创建数据库连接实例
    mssql_instance = Mssql_class(db_ip, db_name, db_user, db_pw)

    try:
        # 连接数据库
        mssql_instance.connect()

        # 根据NEVs参数选择不同的查询模板和参数
        if laneno < 50 or (laneno > 100 and laneno < 150):
            # 入口车道
            if is_NEVs.lower() == 'true':
                print("获取入口---车道新能源车牌url")
                base_query = """      
                           SELECT vehiclesignid, RIGHT('0' + CAST(MONTH(entime) AS VARCHAR(2)), 2) AS MonthValue      
                           FROM enpass WITH (NOLOCK)       
                           WHERE enstationid = ? AND entolllaneid = ? AND entime BETWEEN ? AND ? and vehicleid LIKE ('__[A-Z]%') AND LEN(vehicleid)=10   
                           ORDER BY entime DESC      
                       """
            else:
                base_query = """      
                                  SELECT vehiclesignid, RIGHT('0' + CAST(MONTH(entime) AS VARCHAR(2)), 2) AS MonthValue      
                                  FROM enpass WITH (NOLOCK)      
                                  WHERE enstationid = ? AND entolllaneid = ? AND entime BETWEEN ? AND ?    
                                  ORDER BY entime DESC      
                              """

            query_params = (tollstationid, tolllaneid, starttime, endtime)
        else:
            # 出口车道
            if is_NEVs.lower() == 'true':
                print("获取出口---车道新能源车牌url")
                base_query = """      
                           SELECT vehiclesignid, RIGHT('0' + CAST(MONTH(extime) AS VARCHAR(2)), 2) AS MonthValue, extime      
                           FROM expass WITH (NOLOCK)      
                           WHERE exstationid = ? AND extolllaneid = ? AND extime BETWEEN ? AND ? and vehicleid LIKE ('__[A-Z]%') AND LEN(vehicleid)=10     

                           UNION ALL      

                           SELECT vehiclesignid, RIGHT('0' + CAST(MONTH(extime) AS VARCHAR(2)), 2) AS MonthValue, extime      
                           FROM otherTrans WITH (NOLOCK)      
                           WHERE exstationid = ? AND extolllaneid = ? AND extime BETWEEN ? AND ?  and exvehicleid LIKE ('__[A-Z]%') AND LEN(exvehicleid)=10    

                           ORDER BY MonthValue DESC, extime DESC;      
                       """
            else:
                base_query = """      
                                   SELECT vehiclesignid, RIGHT('0' + CAST(MONTH(extime) AS VARCHAR(2)), 2) AS MonthValue, extime      
                                   FROM expass WITH (NOLOCK)      
                                   WHERE exstationid = ? AND extolllaneid = ? AND extime BETWEEN ? AND ?   

                                   UNION ALL      

                                   SELECT vehiclesignid, RIGHT('0' + CAST(MONTH(extime) AS VARCHAR(2)), 2) AS MonthValue, extime      
                                   FROM otherTrans WITH (NOLOCK)      
                                   WHERE exstationid = ? AND extolllaneid = ? AND extime BETWEEN ? AND ?  
                                   ORDER BY MonthValue DESC, extime DESC;      
                               """

            query_params = (tollstationid, tolllaneid, starttime, endtime,
                            tollstationid, tolllaneid, starttime, endtime)

        # 执行查询
        results = mssql_instance.execute_query(base_query, query_params)

        if not results:
            logger.warning(f"未查询到图片数据: station={tollstationid}, lane={tolllaneid}")
            return JsonResponse({'message': '未找到图片数据', 'data': []}, status=404)

        # 构建图片URL列表
        vehiclesignid_urls = []
        vehlist_base_url = "https://10.88.188.23/lanepic{}/{}"

        for item in results:
            try:
                month_value = item[1]  # MonthValue
                vehicle_sign_id = item[0]  # vehiclesignid
                vehiclesignid_url = vehlist_base_url.format(month_value, vehicle_sign_id)
                vehiclesignid_urls.append(vehiclesignid_url)
            except (IndexError, TypeError) as e:
                logger.error(f"处理结果行时出错: {e}, row: {item}")
                continue

        logger.info(f"成功获取 {len(vehiclesignid_urls)} 张图片URL")

        response_data = {
            'message': '更新图片连接成功！',
            'data': vehiclesignid_urls,
            'count': len(vehiclesignid_urls)
        }
        return JsonResponse(response_data, status=200)

    except Exception as e:
        logger.exception(f"查询图片URL时发生未知错误: {e}")
        return JsonResponse({'error': f'服务器错误: {str(e)}'}, status=500)
    finally:
        mssql_instance.disconnect()  # 确保关闭连接


