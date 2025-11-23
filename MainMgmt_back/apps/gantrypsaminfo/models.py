from django.db import models

class Gantrypsaminfo(models.Model):
    # 门架psam卡信息
    # ('S003944001019020040', '新联东互通与南沙港快速立交连接处-新联工业园', 'K43+800', '4D2913', '2', '5', '2144000448F4',
    #  '44010201000000280820', '正常')

    # tollid 21，position 2，pilenumber 3，rsuid，15，controlid 20，channelid,psamno 20,statusName
    tollid = models.CharField(verbose_name="收费单元编号", max_length=30)
    position = models.CharField(verbose_name="门架区间", max_length=32)
    pilenumber = models.CharField(verbose_name="门架桩号", max_length=16)
    rsuid = models.CharField(verbose_name="RSUID", max_length=16)
    controlid = models.SmallIntegerField(verbose_name="控制器ID", null=True, blank=True)
    channelid = models.SmallIntegerField(verbose_name="通道号", null=True, blank=True)
    psamno = models.CharField(verbose_name="PSAM卡号", max_length=20, primary_key=True)
    statusName = models.CharField(verbose_name="PSAM状态", max_length=16)
    first_createtime = models.DateTimeField(verbose_name="最初获取时间",null=True, blank=True)
    last_createtime = models.DateTimeField(verbose_name="最后获取时间", null=True, blank=True)
    mem = models.CharField(verbose_name="备注", max_length=200, null=True, blank=True)