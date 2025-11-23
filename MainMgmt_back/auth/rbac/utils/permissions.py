# rbac/utils/rbac_permission.py
from typing import Set
from auth.sysuser.models import opsUser          # 用户模型
from auth.sysrole.models import SysUserRole
from auth.permission.models import SysPermission

def get_user_perms(user: opsUser) -> Set[str]:
    """
    获取当前用户拥有的全部权限字符串（角色关联权限）
    返回: {'user:list', 'user:resetpwd', ...}
    """
    # 1. 先拿到用户所有角色 ID
    role_ids = (
        SysUserRole.objects.filter(user=user)
                          .values_list('role_id', flat=True)
    )

    # 2. 再取这些角色拥有的权限字符串
    perms = (
        SysPermission.objects
                     .filter(sysrolepermission__role_id__in=role_ids)
                     .values_list('code', flat=True)
                     .distinct()
    )
    return set(perms)