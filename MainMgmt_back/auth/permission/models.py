from auth.sysrole.models import *
from auth.sysmenu.models import *

class SysPermission(models.Model):
    """
    权限模型，用于控制具体操作（按钮级别）
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True, verbose_name="权限名称")
    code = models.CharField(max_length=50, unique=True, verbose_name="权限标识")  # 例如：'menu:add', 'menu:delete'
    menu = models.ForeignKey(SysMenu, related_name='permissions', on_delete=models.CASCADE)
    request_method = models.CharField(max_length=10, verbose_name="请求方式", choices=[
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('DELETE', 'DELETE')
    ])
    url_path = models.CharField(max_length=200, verbose_name="接口地址")
    remark = models.CharField(max_length=200, null=True, blank=True,verbose_name="备注")

    class Meta:
        db_table = "sys_permission"

class SysRolePermission(models.Model):
    """
    角色权限关联模型
    """
    id = models.AutoField(primary_key=True)
    role = models.ForeignKey(SysRole, on_delete=models.CASCADE)
    permission = models.ForeignKey(SysPermission, on_delete=models.CASCADE)

    class Meta:
        db_table = "sys_role_permission"