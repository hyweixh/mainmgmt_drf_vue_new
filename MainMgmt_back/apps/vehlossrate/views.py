import time
from django.conf import settings
from django.http import JsonResponse
from rest_framework import viewsets, status
from .serializers import VehlossrateSerializer
from .models import Vehlossrate
from rest_framework.response import Response
from utils.databaseclass import Mssql_class
import pymssql

class VehlossrateViewSet(viewsets.ModelViewSet):
    queryset = Vehlossrate.objects.all().order_by('tolllaneid')
    serializer_class = VehlossrateSerializer

    def get_queryset(self):
        stationno = self.request.query_params.get('stationno')
        per1 = self.request.query_params.get('per1')  # per1总识别率
        queryset = self.queryset

        if stationno:
            queryset = queryset.filter(stationno=stationno)
        if per1:
            # queryset = queryset.filter(per1__lt=per1)  # 小于
            queryset = queryset.filter(per1__lte=per1)  # 小于或等于

        return queryset

    # 重写create方法以处理创建逻辑
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # 可以在这里添加任何额外的创建逻辑，比如设置默认字段值
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

# 从mssql获取门架psam卡信息
def get_Vehlossrate_info(request):
    db_ip = settings.MSSQL_SERVER
    db_name = settings.MSSQL_DATABASE
    db_user = settings.MSSQL_USER
    db_pw = settings.MSSQL_PW

    # 实例化 Mssql_class
    mssql_instance = Mssql_class(db_ip, db_name, db_user, db_pw)

    try:
        starttime_str = request.GET.get('starttime', '2020-01-01 00:00:00')
        endtime_str = request.GET.get('endtime', '2024-01-01 00:00:00')
        is_NEVs = request.GET.get('is_NEVs', 'false')
        curlogin_user = request.user

        query_params = (starttime_str, endtime_str)

        # curlogin_user获取的是admin，但是下下面的更新中用'inspector': curlogin_user会提示其值为“<UserInfo: admin>”
        # print("kaishishijian :", starttime_str, endtime_str, is_NEVs, curlogin_user)

        # 连接数据库
        mssql_instance.connect()
        # 删除 Vehlossrate 表内容
        Vehlossrate.objects.all().delete()
        if is_NEVs == 'true':
            query = f"exec wh_proc_vehlossrate_nev @StartDate= ? , @EndDate= ? "
        else:
            query = f"exec wh_proc_vehlossrate @StartDate= ?, @EndDate= ? "

        vehlossrate_info = mssql_instance.execute_query(query, query_params)
        # ('S00394400100104010050', 'S0039440010010', 3, 3, 'MTC', '10.144.160.30', 297, 296, 283, '99.66', '95.29', '95.61')
        # print(vehlossrate_info)
        if vehlossrate_info is not None:
            # 准备要保存或更新的数据
            current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

            for row in vehlossrate_info:
                # 准备数据字典
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
                    'starttime': starttime_str,
                    'endtime': endtime_str,
                    # inspector 字段被设置为 request.user，这在 Django 中通常是一个用户模型实例（如 User）
                    # 在使用用户模型中的某个字符串属性，需要如此引用curlogin_user.realname，而不是整个用户对象。
                    'inspector': curlogin_user.realname,
                    'inspecttime': current_time,
                }

                vehlossrate_info, created = Vehlossrate.objects.update_or_create(
                        tolllaneid=data['tolllaneid'],
                        isconfirm=0,
                        defaults=data
                    )
            # 所有数据都保存或更新成功后返回响应
            return JsonResponse({'message': '更新车牌识别率成功！'}, status=200)

        else:
            # 如果 psam_info 为 None，则返回没有检索到数据的错误
            return JsonResponse({'error': 'No data retrieved'}, status=404)

    except Exception as e:
        # 捕获异常并返回错误响应
        print(f"Error in get_vehlossrate_info: {e}")
        return JsonResponse({'error': '更新车牌识别率失败'}, status=500)

    finally:
        # 无论是否发生异常，都断开数据库连接
        mssql_instance.disconnect()

# 获取车道图片连接
def get_vehlossrate_imageUrl(request):
    # print(request.GET)
    tollstationid = request.GET.get('tollstationid')
    tolllaneid = request.GET.get('tolllaneid')
    laneno = int(request.GET.get('laneno', 0))
    starttime = request.GET.get('starttime')
    endtime = request.GET.get('endtime')
    # is_NEVs 是通过 request.GET.get('is_NEVs') 获取的，它将默认为 None 而不是 False
    is_NEVs = request.GET.get('is_NEVs')

    print("后台获取：", tollstationid, tolllaneid, starttime, endtime, laneno, is_NEVs)

    db_ip = settings.MSSQL_SERVER
    db_name = settings.MSSQL_DATABASE
    db_user = settings.MSSQL_USER
    db_pw = settings.MSSQL_PW

    # 创建数据库连接实例
    mssql_instance = Mssql_class(db_ip, db_name, db_user, db_pw)

    # 连接数据库（假设 Mssql_class 的 connect 方法负责建立连接）
    mssql_instance.connect()
    query_params_part1 = (tollstationid, tolllaneid, starttime, endtime)
    # nevs_params = " and vehicleid LIKE ('__[A-Z]%') AND LEN(vehicleid)=10"
    # 根据 laneno 和 is_NEVs 动态构建查询模板和参数
    if laneno < 50 or (laneno > 100 and laneno < 150):

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

        query_template = base_query
        query_params = query_params_part1
    else:# 出口车道
        if is_NEVs.lower() == 'true':
            print("获取出口车道新能源车牌url")
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
                                   WHERE exstationid = ? 
                                   AND extolllaneid = ? 
                                   AND extime BETWEEN ? AND ?   

                                   UNION ALL      

                                   SELECT vehiclesignid, RIGHT('0' + CAST(MONTH(extime) AS VARCHAR(2)), 2) AS MonthValue, extime      
                                   FROM otherTrans WITH (NOLOCK)      
                                   WHERE exstationid = ? 
                                   AND extolllaneid = ? 
                                   AND extime BETWEEN ? AND ?  
                                   ORDER BY MonthValue DESC, extime DESC;      
                               """

        query_template = base_query
        query_params = query_params_part1 + query_params_part1
    # 确保 query_template 总是被赋值
    # print("query_template:", query_template)
    # print("query_params:", query_params)
    try:
        # 假设 execute_query 方法能够正确处理参数化查询
        results = mssql_instance.execute_query(query_template, query_params)
        # print("results=",results)
        vehiclesignid_urls = []
        for item in results:
            vehlist_base_url = "https://10.88.188.23/lanepic{}/{}"
            vehiclesignid_url = vehlist_base_url.format(item[1], item[0])
            vehiclesignid_urls.append(vehiclesignid_url)
        # print("vehiclesignid_urls::", vehiclesignid_urls)

        response_data = {'message': '更新图片连接成功！', 'data': vehiclesignid_urls}
        return JsonResponse(response_data, status=201)
    except Exception as e:
        # 记录错误或返回错误响应
        # print(f"Error executing query: {e}")
        return JsonResponse({'message': 'Error executing query'}, status=500)
    finally:
        mssql_instance.disconnect()  # 确保在返回之前关闭连接


