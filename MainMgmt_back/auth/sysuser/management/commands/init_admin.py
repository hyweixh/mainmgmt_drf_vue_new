# auth/sysuser/management/commands/init_admin.py
"""
初始化 admin 账号并赋予全部菜单+权限
shell 快速验证：
    from auth.sysuser.models import opsUser
    u = opsUser.objects.get(username='admin')
    [u.roles.all(), u.roles.first().sysrolemenu_set.count(), u.roles.first().sysrolepermission_set.count()]
"""
from django.core.management.base import BaseCommand
from django.db import transaction, IntegrityError

from auth.sysuser.models import opsUser
from auth.sysrole.models import SysRole, SysUserRole
from auth.sysmenu.models import SysMenu, SysRoleMenu
from auth.permission.models import SysPermission, SysRolePermission


class Command(BaseCommand):
    help = "初始化 admin 账号并赋予全部菜单+权限"

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            type=str,
            default="admin",
            help="超级管理员用户名（默认 admin）",
        )
        parser.add_argument(
            "--password",
            type=str,
            default="admin123",
            help="超级管理员密码（默认 admin123）",
        )
        parser.add_argument(
            "--email",
            type=str,
            default="admin@example.com",
            help="超级管理员邮箱（默认 admin@example.com）",
        )

    def handle(self, *args, **options):
        username = options["username"]
        password = options["password"]
        email    = options["email"]

        with transaction.atomic():
            # 1. 创建或获取 admin 用户
            admin_user, created = opsUser.objects.get_or_create(
                username=username,
                defaults={
                    "email": email,
                    "realname": "超级管理员",
                    "status": 1,  # ACTIVE
                },
            )
            if created:
                admin_user.set_password(password)
                admin_user.save()
                self.stdout.write(self.style.SUCCESS(f"✅ 创建用户<{username}>成功"))
            else:
                self.stdout.write(self.style.WARNING(f"⚠️  用户<{username}>已存在，跳过创建"))

            # 2. 创建或获取“超级管理员”角色（防 1062 冲突）
            try:
                super_role = SysRole.objects.get(code="super_admin")
                self.stdout.write(self.style.WARNING("⚠️  角色<超级管理员>已存在，清空后重新绑定"))
            except SysRole.DoesNotExist:
                try:
                    super_role = SysRole.objects.create(
                        code="super_admin",
                        name="超级管理员",
                        remark="系统初始超级角色，拥有全部菜单与权限",
                    )
                    self.stdout.write(self.style.SUCCESS("✅ 创建角色<超级管理员>成功"))
                except IntegrityError:          # 并发场景下万一冲突
                    super_role = SysRole.objects.get(code="super_admin")

            # 清空旧绑定，防止脏数据
            SysRoleMenu.objects.filter(role=super_role).delete()
            SysRolePermission.objects.filter(role=super_role).delete()

            # 3. 绑定所有菜单
            all_menus = SysMenu.objects.all()
            SysRoleMenu.objects.bulk_create(
                [SysRoleMenu(role=super_role, menu=menu) for menu in all_menus],
                ignore_conflicts=True,
            )
            self.stdout.write(self.style.SUCCESS(f"✅ 已绑定 {len(all_menus)} 个菜单"))

            # 4. 绑定所有权限
            all_permissions = SysPermission.objects.all()
            SysRolePermission.objects.bulk_create(
                [SysRolePermission(role=super_role, permission=perm) for perm in all_permissions],
                ignore_conflicts=True,
            )
            self.stdout.write(self.style.SUCCESS(f"✅ 已绑定 {len(all_permissions)} 个权限"))

            # 5. 给用户赋予超级角色
            _, created = SysUserRole.objects.get_or_create(
                user=admin_user, role=super_role
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"✅ 已将角色<超级管理员>赋给用户<{username}>"))
            else:
                self.stdout.write(self.style.WARNING(f"⚠️  用户<{username}>已拥有角色<超级管理员>"))

        self.stdout.write(self.style.SUCCESS("🎉 初始化完成！"))