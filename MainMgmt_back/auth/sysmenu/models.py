from auth.sysrole.models import *


class SysMenu(models.Model):
    """
    菜单表
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, null=True,unique=True, verbose_name="菜单名称")
    text = models.CharField(max_length=50, unique=True,verbose_name="菜单标签")
    icon = models.CharField(max_length=100, null=True, verbose_name="菜单图标")
    parent_id = models.IntegerField(verbose_name="父菜单ID")
    order_num = models.IntegerField(verbose_name="显示顺序")
    path = models.CharField(max_length=200, verbose_name="路由地址")
    component = models.CharField(max_length=255, null=True, blank=True,verbose_name="组件路径")
    menu_type = models.CharField(max_length=1, verbose_name="菜单类型（M目录 C菜单 F按钮）")
    perms = models.CharField(max_length=100, null=True,blank=True, verbose_name="权限标识")
    create_time = models.DateField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    remark = models.CharField(max_length=500, null=True, blank=True,verbose_name="备注")

    def __lt__(self, other):
        # 按 order_num 排序
        return self.order_num < other.order_num

    class Meta:
        db_table = "sys_menu"
        # 建议加唯一索引，防脏数据（若已建可忽略）
        constraints = [
            models.UniqueConstraint(
                fields=['parent_id', 'order_num'],
                name='uniq_parent_order'
            )
        ]

class SysRoleMenu(models.Model):
    """
    角色菜单关联类
    """
    id = models.AutoField(primary_key=True)
    role = models.ForeignKey(SysRole, on_delete=models.CASCADE)
    menu = models.ForeignKey(SysMenu, on_delete=models.CASCADE)

    class Meta:
        db_table = "sys_role_menu"




