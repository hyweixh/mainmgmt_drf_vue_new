from datetime import datetime
import threading
from django.conf import settings
from django.http import JsonResponse
from .models import Holidayfree
from rest_framework import viewsets, status
from .serializers import HolidayfreeSerializer
from rest_framework.response import Response
from utils.Telnetport import TelnetClient
# from django.utils import timezone
from utils.databaseclass import Mssql_class, Firebird_class

class HolidayfreeViewSet(viewsets.ModelViewSet):
    queryset = Holidayfree.objects.all()
    serializer_class = HolidayfreeSerializer

    # def get_queryset(self):
    #     return Holidayfree.objects.all().order_by('stationno', 'laneno')

    def get_queryset(self):
        inspectresult = self.request.query_params.get('inspectresult')
        starttime = self.request.query_params.get('starttime')
        queryset = self.queryset

        if inspectresult:
            queryset = queryset.filter(inspectresult__icontains=inspectresult)
        if starttime:
            queryset = queryset.filter(starttime__icontains=starttime)

        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # 可以在这里添加任何额外的创建逻辑，比如设置默认字段值
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

def connect_to_firebird(lane_info):
    laneip = lane_info[3]
    data = Firebird_class(laneip, 3050, 'sysdba', 'hyits', 'lanepara')
    try:
        cursor = data.connect()
        return data, cursor
    except Exception as e:
        print(f"Failed to connect to Firebird database: {e}")
        return None, None

def update_or_create_holidayfree(lane_info, holiday_data=None, inspect_result='网络故障'):
    tollid, stationno, laneno, lanecomputerip, lanetype, cur_name = lane_info
    # print("lane_info:", lane_info)
    defaults = {
        'tollid': tollid,
        'stationno': stationno,
        'laneno': laneno,
        'lanecomputerip': lanecomputerip,
        'lanetype': lanetype,
        'verid': '000',
        'starttime': datetime(2000, 1, 1, 0, 0),
        'overtime': datetime(2000, 1, 1, 0, 0),
        # 'starttime': timezone.make_aware(datetime(2000, 1, 1, 0, 0, 0)),  # 关键：添加时区
        # 'overtime': timezone.make_aware(datetime(2000, 1, 1, 0, 0, 0)),  # 关键：添加时区
        'inspector': cur_name,
        # 'inspecttime': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'inspecttime':  datetime.now(),
        'inspectresult': inspect_result,
    }
    # print("初始的defaults数据:", defaults)  # 打印初始的 defaults 字典
    if holiday_data is not None and len(holiday_data) > 0:
        lane_verid, lane_starttime, lane_overtime = holiday_data[0]   # 直接从元组中获取值
        # 将字符串转换为 datetime 对象（确保字符串格式与 parse 方法兼容）

        defaults.update({
                        'verid': str(lane_verid),
                        # 'starttime': datetime.strptime(lane_starttime, "%Y-%m-%d %H:%M:%S"),
                        # 'overtime': datetime.strptime(lane_overtime, "%Y-%m-%d %H:%M:%S"),
                        'starttime': lane_starttime,
                        'overtime': lane_overtime,
                        'inspectresult': "获取成功",
                        })
        # print("更新后的Defaults:", defaults)  # 打印调试信息

    Holidayfree.objects.update_or_create(
                                        tollid=tollid,
                                        isconfirm=False,
                                        defaults=defaults
                                        )
    # else:
    #     Holidayfree.objects.update_or_create(
    #         tollid=tollid,
    #         isconfirm=False,
    #         defaults=defaults
    #     )
def query_lanefddb_insmysql(laneinfo):
    inspector = None  # 假设需要定义这个变量，或者从某处获取
    try:
        # 尝试连接Telnet
        tel_client = TelnetClient(laneinfo[3], 3050)
        tel_rec = tel_client.connect()
        if not tel_rec:
            raise Exception("telnet车道3050端口失败！")

            # 查询Firebird数据库
        firebird_data, cursor = connect_to_firebird(laneinfo)
        if firebird_data is None:
            raise Exception("连接车道firebird数据库失败！")

        fbquery_Str = 'SELECT verid, starttime, overtime FROM holidayfree'
        holidayfree_para = firebird_data.execute_query(fbquery_Str)
        # print(holidayfree_para)

        # 更新或创建Holidayfree记录
        update_or_create_holidayfree(laneinfo, holidayfree_para if holidayfree_para else None)

        # 关闭数据库连接
        firebird_data.close_connection()

    except Exception as e:
        # print(f"An error occurred: {e}")
        update_or_create_holidayfree(laneinfo, inspect_result='获取失败')

def holidayfree_update(request):
    # print('-----------')
    db_ip = settings.MSSQL_SERVER
    db_name = settings.MSSQL_DATABASE
    db_user = settings.MSSQL_USER
    db_pw = settings.MSSQL_PW
    cur_name = request.user.realname

    query = f'exec wh_proc_tolllaneinfo'
    query_params = ()  # 不能赋予‘’
    mssql_instance = Mssql_class(db_ip, db_name, db_user, db_pw)
    # 连接数据库
    mssql_instance.connect()
    resList = mssql_instance.execute_query(query, query_params)
    # 从mssql数据库获取车道信息

    # print(resList)
    threads = []
    for item in resList:
        #laneip = item[3]
        laneinfo = (item[0], item[1], item[2], item[3], item[4], cur_name)
        threads.append(
            threading.Thread(target=query_lanefddb_insmysql,
                             args=(laneinfo, ))
        )
    for thread in threads:
        thread.start()
    # 等待所有线程完成
    for thread in threads:
        thread.join()

    return JsonResponse({'message': '获取车道免费参数成功！'}, status=201)


