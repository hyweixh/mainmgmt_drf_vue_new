from django.db import models

class Holidayfree(models.Model):
    tollid = models.CharField(verbose_name="收费单元编号", max_length=25)
    stationno = models.SmallIntegerField(verbose_name="收费站编号")
    laneno = models.SmallIntegerField(verbose_name="车道编号")
    lanecomputerip = models.GenericIPAddressField(verbose_name="设备IP")
    lanetype = models.CharField(verbose_name="车道类型", max_length=16)
    verid = models.CharField(verbose_name="版本号", max_length=16, null=True, blank=True)
    starttime = models.DateTimeField(verbose_name="免费开始时间", null=True, blank=True)
    overtime = models.DateTimeField(verbose_name="免费结束时间", null=True, blank=True)
    inspector = models.CharField(verbose_name="检查人员", max_length=32)
    inspecttime = models.DateTimeField(verbose_name="检查时间", null=True, blank=True)
    inspectresult = models.CharField(verbose_name="检查结果", max_length=32)
    confirmer = models.CharField(verbose_name="确认人员", max_length=32, null=True, blank=True)
    confirmdatetime = models.DateTimeField(verbose_name="确认时间", null=True, blank=True)
    isconfirm = models.BooleanField(verbose_name='是否确认', default=False)

    class Meta:
        # ✅ 添加默认排序（按 'stationno', 'laneno' 升序）
        ordering = ['stationno', 'laneno']
