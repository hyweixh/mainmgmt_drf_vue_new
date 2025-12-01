from django.db import models

class Pingdevices(models.Model):
    """Ping设备检查结果"""
    position = models.CharField(verbose_name="桩号", max_length=32)
    devicename = models.CharField(verbose_name="设备名称", max_length=50)
    deviceip = models.GenericIPAddressField(verbose_name="设备IP")

    # ✅ 修改：允许devicetype为空
    devicetype = models.ForeignKey(
        'devicemgmt.DeviceType',
        verbose_name="设备类型",
        on_delete=models.SET_NULL,  # 外键删除时设为null
        related_name='ping_devices',
        null=True,  # ✅ 数据库允许为空
        blank=True  # ✅ 表单验证允许为空
    )

    inspectresult = models.CharField(
        verbose_name="检查结果",
        max_length=12,
        choices=[('online', '在线'), ('offline', '离线'), ('error', '检查失败')]
    )
    inspector = models.CharField(verbose_name="检查人员", max_length=32)
    inspecttime = models.DateTimeField(verbose_name="检查时间", auto_now_add=True)
    confirmer = models.CharField(verbose_name="确认人员", max_length=32, null=True, blank=True)
    confirmdatetime = models.DateTimeField(verbose_name="确认时间", null=True, blank=True)
    isconfirm = models.BooleanField(verbose_name='是否确认', default=False)
    error_desc = models.CharField(verbose_name="故障描述", max_length=100, null=True, blank=True)
    error_proc = models.CharField(verbose_name="故障处理", max_length=100, null=True, blank=True)
    response_time = models.FloatField(verbose_name="响应时间(ms)", null=True, blank=True)
    task_id = models.CharField(verbose_name="任务ID", max_length=64, db_index=True, null=True, blank=True)

    class Meta:
        db_table = 'ping_devices'
        ordering = ['-deviceip']
        indexes = [
            models.Index(fields=['deviceip', 'inspecttime']),
            models.Index(fields=['task_id']),
        ]
        # ✅ 添加唯一约束（可选，确保数据完整性）
        constraints = [
            models.UniqueConstraint(
                fields=['deviceip'],
                name='unique_deviceip_per_record',
                # condition=Q(task_id__isnull=False)  # 可选：只约束有task_id的记录
            )
        ]