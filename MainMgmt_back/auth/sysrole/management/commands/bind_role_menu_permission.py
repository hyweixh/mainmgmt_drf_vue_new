# auth/sysrole/management/commands/bind_role_menu_permission.py
"""
给配置里所有角色统一绑定
    python manage.py bind_role_menu_permission
只给某个角色补绑（调试时常用）
    python manage.py bind_role_menu_permission --role ordinary_admin

三个初始化菜单，人员，角色，权限的执行步骤
1. 写入菜单+权限
   python manage.py init_menu_and_permission
2. 绑定角色<->菜单<->权限
   python manage.py bind_role_menu_permission
3. 创建超级管理员账号并自动拥有超级管理员角色
   python manage.py init_admin
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from auth.sysrole.models import SysRole
from auth.sysmenu.models import SysMenu, SysRoleMenu
from auth.permission.models import SysPermission, SysRolePermission


class Command(BaseCommand):
    help = "批量绑定角色-菜单-权限（配置化）"

    # -------------------- 配置区 --------------------
    # 外层 key = 角色 code，内层是两个 list
    BIND_CFG = {
        "super_admin": {  # 超级管理员
            # 菜单 text 列表（必须和 SysMenu.text 完全一致）
            "menus": ["系统管理", "用户管理", "角色管理", "菜单管理", "主页"],
            "permissions": ["*"],  # "*" 代表绑定这些菜单下的所有权限
        },
        "ordinary_admin": {  # 普通管理员
            "menus": ["系统管理", "用户管理"],
            "permissions": [
                "user:list",
                "user:add",
                "user:edit",
                "user:delete",
                "user:admin-reset-password",
            ],
        },
    }
    # ------------------ 配置结束 ------------------

    def add_arguments(self, parser):
        parser.add_argument(
            "--role",
            type=str,
            help="只给指定角色 code 绑定（默认全部）",
        )

    def handle(self, *args, **options):
        filter_role = options["role"]
        cfg = {filter_role: self.BIND_CFG[filter_role]} if filter_role else self.BIND_CFG

        with transaction.atomic():
            for role_code, item in cfg.items():
                role, created = SysRole.objects.get_or_create(
                    code=role_code,
                    defaults={"name": role_code.replace("_", " ").title()},
                )
                status = "新增" if created else "已存在"
                self.stdout.write(self.style.SUCCESS(f"🍀 角色<{role_code}> {status}"))

                # 1. 绑定菜单
                menu_texts = item.get("menus", [])
                menus = SysMenu.objects.filter(text__in=menu_texts)
                if not menus:
                    self.stdout.write(self.style.WARNING(f"⚠️  未找到任何菜单，跳过绑定"))
                    continue
                SysRoleMenu.objects.bulk_create(
                    [SysRoleMenu(role=role, menu=m) for m in menus],
                    ignore_conflicts=True,
                )
                self.stdout.write(self.style.SUCCESS(f"   已绑定 {len(menus)} 个菜单"))

                # 2. 绑定权限
                perm_codes = item.get("permissions", [])
                if "*" in perm_codes:
                    # 绑定这些菜单下的所有权限
                    perms = SysPermission.objects.filter(menu__in=menus)
                else:
                    perms = SysPermission.objects.filter(code__in=perm_codes)
                if not perms:
                    self.stdout.write(self.style.WARNING(f"⚠️  未找到任何权限，跳过绑定"))
                    continue
                SysRolePermission.objects.bulk_create(
                    [SysRolePermission(role=role, permission=p) for p in perms],
                    ignore_conflicts=True,
                )
                self.stdout.write(self.style.SUCCESS(f"   已绑定 {len(perms)} 个权限"))

        self.stdout.write(self.style.SUCCESS("🎉 角色-菜单-权限绑定完成！"))