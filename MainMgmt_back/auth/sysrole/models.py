from auth.sysuser.models import *


# 系统角色类
class SysRole(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, unique=True, blank=False, verbose_name="角色名称")
    code = models.CharField(max_length=100, unique=True, blank=False, verbose_name="角色权限字符串")
    create_time = models.DateField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    remark = models.CharField(max_length=500, null=True, verbose_name="备注")

    class Meta:
        db_table = "sys_role"
        ordering = ['id']

# 系统用户角色关联类
class SysUserRole(models.Model):
    id = models.AutoField(primary_key=True)
    role = models.ForeignKey(SysRole, on_delete=models.CASCADE)
    user = models.ForeignKey(opsUser, on_delete=models.CASCADE)

    class Meta:
        db_table = "sys_user_role"



