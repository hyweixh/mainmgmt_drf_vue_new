from django.db import models
from django.contrib.auth import get_user_model

# 与devicetype有外键关联，需导入get_user_model
DeviceType = get_user_model()


class SubnetType(models.Model):
    '''
    子网信息，通过初始化命令添加
    '''
    subnettypename = models.CharField(verbose_name='子网名称', max_length=16)

class DeviceType(models.Model):
    ''' 设备类型，通过初始化命令添加'''
    devicetypename = models.CharField(verbose_name='设备类型', max_length=16)

    def __str__(self):
        return self.devicetypename
'''
class Absent(models.Model):
    # 1. 标题
    title = models.CharField(max_length=200)
    # 2. 请假详细内容
    request_content = models.TextField()
    # 3. 请假类型（事假、婚假）
    absent_type = models.ForeignKey(AbsentType, on_delete=models.CASCADE, related_name='absents', related_query_name='absents')
    # 如果在一个模型中，有多个字段对同一个模型引用了外键，那么必须指定related_name为不同的值
    # 4. 发起人
    requester = models.ForeignKey(OAUser, on_delete=models.CASCADE, related_name='my_absents', related_query_name='my_absents')
    # 5. 审批人（可以为空）
    responder = models.ForeignKey(OAUser, on_delete=models.CASCADE, related_name='sub_absents', related_query_name='sub_absents', null=True)
    # 6. 状态
    status = models.IntegerField(choices=AbsentStatusChoices, default=AbsentStatusChoices.AUDITING)
    # 7. 请假开始日期
    start_date = models.DateField()
    # 8. 请假结束日期
    end_date = models.DateField()
    # 9. 请假发起时间
    create_time = models.DateTimeField(auto_now_add=True)
    # 10. 审批回复内容
    response_content = models.TextField(blank=True)

    class Meta:
        # -create_time排序(倒序)
        ordering = ('-create_time', )
'''
class DeviceInfo(models.Model):
    """ 设备资产信息表 """
    # unique = True,唯一值
    deviceip= models.GenericIPAddressField(verbose_name="设备IP")
    devicename = models.CharField(verbose_name="设备名称", max_length=50)
    position = models.CharField(verbose_name="安装位置", max_length=32)
    devicetype = models.ForeignKey(to=DeviceType, verbose_name="设备类型", on_delete=models.CASCADE,
                                   related_name='deviceinfo', related_query_name='deviceinfo')
    # devicetype = models.ForeignKey(verbose_name="设备类型", DeviceType, on_delete=models.CASCADE, related_name='deviceinfo',
    #                                related_query_name='deviceinfo')
    devicemanufacture = models.CharField(verbose_name="设备厂商", max_length=50, null=True, blank=True)
    unittype = models.CharField(verbose_name="设备型号", max_length=50, null=True, blank=True)
    deviceserialnumber = models.CharField(verbose_name="设备序列号", max_length=50, null=True, blank=True)
    subnetwork = models.ForeignKey(SubnetType, verbose_name="子网", on_delete=models.CASCADE, related_name='deviceinfo', related_query_name='deviceinfo')
    user1 = models.CharField(verbose_name="用户1", max_length=30, null=True, blank=True)
    pwd1 = models.CharField(verbose_name="密码1", max_length=128, null=True, blank=True)
    user2 = models.CharField(verbose_name="用户2", max_length=30, null=True, blank=True)
    pwd2 = models.CharField(verbose_name="密码2", max_length=128, null=True, blank=True)
    user3 = models.CharField(verbose_name="用户3", max_length=30, null=True, blank=True)
    pwd3 = models.CharField(verbose_name="密码3", max_length=128, null=True, blank=True)
    user4 = models.CharField(verbose_name="用户4", max_length=30, null=True, blank=True)
    pwd4 = models.CharField(verbose_name="密码4", max_length=128, null=True, blank=True)
    mem = models.TextField(verbose_name="备注", max_length=200, null=True, blank=True)
    create_time = models.DateTimeField(auto_now_add=True)
    class Meta:
        # -create_time排序(倒序)
        ordering = ('-create_time',)