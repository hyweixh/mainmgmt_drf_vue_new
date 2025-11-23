from django.db import models
# psam卡管理
class PsamStatus(models.Model):
    ''' psam卡状态，人工维护 '''
    psamstatus = models.CharField(verbose_name='psam卡状态', max_length=16)

    # 通过__str__函数，给关联表返回Psamstatus
    # 否侧返回的是Psamstatus.object(1)
    def __str__(self):
        return self.psamstatus

class LanePsamInfo(models.Model):
    # psam卡信息,psamno为主键，表内无'id'
    # deviceid 21，stationno 2，laneno 3，lanecomputerip，15，terminano 20，psamno 20
    deviceid = models.CharField(verbose_name="收费单元编号", max_length=30)
    stationno = models.SmallIntegerField(verbose_name="收费站编号")
    laneno = models.SmallIntegerField(verbose_name="车道编号")
    lanecomputerip = models.GenericIPAddressField(verbose_name="设备IP")
    terminano = models.CharField(verbose_name="终端编号", max_length=20, null=True, blank=True)
    psamno = models.CharField(verbose_name="PSAM卡卡号", max_length=20, primary_key=True)
    psamstatus = models.ForeignKey(verbose_name="PSAM卡状态", default=1, to="PsamStatus", to_field="id", on_delete=models.CASCADE)
    first_createtime = models.DateTimeField(verbose_name="最初获取时间", null=True, blank=True)
    last_createtime = models.DateTimeField(verbose_name="最后获取时间", null=True, blank=True)
    mem = models.CharField(verbose_name="备注", max_length=200, null=True, blank=True)

    def clean_psamstatus(self):
        # 返回与当前Psaminfo实例关联的Psamstatus的状态名称
        return self.psamstatus.psamstatus
