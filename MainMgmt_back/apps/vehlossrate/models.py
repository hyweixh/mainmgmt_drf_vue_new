from django.db import models


class Vehlossrate(models.Model):
    tolllaneid = models.CharField(verbose_name="国标车道编码", max_length=25, db_index=True)
    stationid = models.CharField(verbose_name="国标站编码", max_length=25, db_index=True)
    stationno = models.SmallIntegerField(verbose_name="收费站编号", db_index=True)
    laneno = models.SmallIntegerField(verbose_name="车道编号")
    lanetypename = models.CharField(verbose_name="车道类型", max_length=16, null=True, blank=True)
    lanecomputerip = models.GenericIPAddressField(verbose_name="设备IP")
    cnt = models.IntegerField(verbose_name="交易数量", null=True, blank=True)
    veh = models.IntegerField(verbose_name="抓拍数量", null=True, blank=True)
    scu = models.IntegerField(verbose_name="识别数量", null=True, blank=True)
    per = models.FloatField(verbose_name="抓拍率", null=True, blank=True)
    per1 = models.FloatField(verbose_name="总识别率", null=True, blank=True)
    per2 = models.FloatField(verbose_name="有牌识别率", null=True, blank=True)

    # 关键修改：CharField → DateTimeField，支持时区
    starttime = models.DateTimeField(verbose_name="开始时间", null=True, blank=True)
    endtime = models.DateTimeField(verbose_name="结束时间", null=True, blank=True)

    inspector = models.CharField(verbose_name="检查人员", max_length=32, db_index=True)

    # 建议修改：CharField → DateTimeField
    inspecttime = models.DateTimeField(verbose_name="检查时间", null=True, blank=True)

    isconfirm = models.BooleanField(verbose_name='是否确认', default=False, db_index=True)

    class Meta:
        # 复合唯一约束：确保同一车道同一时间范围只有一条未确认记录
        unique_together = [
            ['tolllaneid', 'starttime', 'endtime', 'isconfirm']
        ]

        # 性能优化：创建复合索引（如果unique_together已包含，可省略）
        indexes = [
            models.Index(fields=['tolllaneid', 'starttime', 'endtime']),
            models.Index(fields=['stationno', 'laneno']),
        ]

    def __str__(self):
        return f"{self.tolllaneid} - {self.starttime}"

    # 新增方法：格式化显示时间（兼容前端）
    def starttime_formatted(self):
        return self.starttime.strftime('%Y-%m-%d %H:%M:%S') if self.starttime else ''

    def endtime_formatted(self):
        return self.endtime.strftime('%Y-%m-%d %H:%M:%S') if self.endtime else ''