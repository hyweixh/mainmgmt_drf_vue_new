# coding:utf-8
# auth/sysmenu/management/commands/init_menu_and_permission.py
"""
    直接增量写入（推荐第一次）
    python manage.py init_menu_and_permission

    想从头开始（会清空旧数据）
    python manage.py init_menu_and_permission --flush
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from auth.sysmenu.models import SysMenu
from auth.permission.models import SysPermission


class Command(BaseCommand):
    help = "按 sys_menu 真实数据初始化菜单与按钮权限"

    def add_arguments(self, parser):
        parser.add_argument("--flush", action="store_true", help="先清空旧数据再写入")

    # --------------- 与 sys_menu 完全对应 ---------------
    MENU_CFG = [
        # 一级
        {"text": "主页", "name": "home", "icon": "home", "parent_text": None, "order_num": 10,
         "path": "/", "menu_type": "C"},
        {"text": "系统管理", "name": "sys", "icon": "system", "parent_text": None, "order_num": 9999,
         "path": "/sys", "menu_type": "M"},

        # 二级（挂到“系统管理”下）
        {"text": "用户管理", "name": "user", "icon": "user", "parent_text": "系统管理", "order_num": 1,
         "path": "/sys/user", "menu_type": "C"},
        {"text": "角色管理", "name": "role", "icon": "role", "parent_text": "系统管理", "order_num": 2,
         "path": "/sys/role", "menu_type": "C"},
        {"text": "菜单管理", "name": "menu", "icon": "menu", "parent_text": "系统管理", "order_num": 3,
         "path": "/sys/menu", "menu_type": "C"},
    ]
    # 按钮权限配置（根据 sys_permission 内容调整）
    PERM_CFG = {
        "用户管理": [
            {"name": "查询用户列表", "code": "user:list", "method": "GET", "url_path": "/api/auth/users"},
            {"name": "添加用户", "code": "user:add", "method": "POST", "url_path": "/api/auth/users"},
            {"name": "修改用户", "code": "user:edit", "method": "PUT", "url_path": "/api/auth/users/{userId}"},
            {"name": "删除用户", "code": "user:delete", "method": "DELETE", "url_path": "/api/auth/users/{userId}"},
            {
                "name": "超级用户重置密码",
                "code": "user:resetpwd",
                "method": "POST",
                "url_path": "/api/auth/changePassword",
            },
        ],
        "角色管理": [
            {"name": "查询角色列表", "code": "role:list", "method": "GET", "url_path": "/api/role/roles"},
            {"name": "添加角色", "code": "role:add", "method": "POST", "url_path": "/api/role/roles"},
            {"name": "修改角色", "code": "role:edit", "method": "PUT", "url_path": "/api/role/roles/{roleid}"},
            {"name": "删除角色", "code": "role:delete", "method": "DELETE", "url_path": "/api/role/roles/{roleid}"},
            {"name": "分配角色权限", "code": "role:permission", "method": "POST", "url_path": "/api/role/assign_menu"},
            {"name": "查询角色菜单列表", "code": "role:menuList", "method": "GET", "url_path": "/api/role/role_menus/{roleId}"},
        ],
        "菜单管理": [
            {"name": "查看菜单列表", "code": "menu:list", "method": "GET", "url_path": "/api/menu/menus"},
            {"name": "添加菜单", "code": "menu:add", "method": "POST", "url_path": "/api/menu/menus"},
            {"name": "修改菜单", "code": "menu:edit", "method": "PUT", "url_path": "/api/menu/menus/{menuId}"},
            {"name": "删除菜单", "code": "menu:delete", "method": "DELETE", "url_path": "/api/menu/menus/{menuId}"},
            {"name": "查询权限列表", "code": "permission:list", "method": "GET", "url_path": "/api/permission/permissions"},
            {"name": "添加权限", "code": "permission:add", "method": "POST", "url_path": "/api/permission/permissions"},
            {"name": "修改权限", "code": "permission:edit", "method": "PUT", "url_path": "/api/permission/permissions/{permissionId}"},
            {"name": "删除权限", "code": "permission:delete", "method": "DELETE", "url_path": "/api/permission/permissions/{permissionId}"},
        ],
    }

    # ------------------------------------------------------

    def handle(self, *args, **options):
        flush = options["flush"]
        with transaction.atomic():
            if flush:
                confirm = input("⚠️  将清空所有菜单与权限！输入大写 YES 确认：")
                if confirm != "YES":
                    self.stdout.write(self.style.WARNING("❌ 已取消"))
                    return
                SysPermission.objects.all().delete()
                SysMenu.objects.all().delete()
                self.stdout.write(self.style.SUCCESS("🗑️  已清空旧数据"))

            # 先写一级，再写二级，保证 parent_id 正确
            text_to_menu = {}
            for item in self.MENU_CFG:
                parent_text = item.get("parent_text")
                parent_id = 0 if parent_text is None else text_to_menu[parent_text].id
                menu, created = SysMenu.objects.get_or_create(
                    text=item["text"],
                    defaults={
                        "name": item["name"],
                        "icon": item["icon"],
                        "parent_id": parent_id,
                        "order_num": item["order_num"],
                        "path": item["path"],
                        "component": item.get("component"),
                        "menu_type": item["menu_type"],
                        "perms": item.get("perms"),
                    },
                )
                status = "新增" if created else "已存在"
                self.stdout.write(self.style.SUCCESS(f"🍀 {status}菜单：{item['text']}"))
                text_to_menu[item["text"]] = menu

            # 权限绑定逻辑不变（略）
            for menu_text, perm_list in self.PERM_CFG.items():
                menu = text_to_menu.get(menu_text)
                if not menu:
                    self.stdout.write(self.style.WARNING(f"⚠️  找不到菜单<{menu_text}>，跳过其权限"))
                    continue
                for perm in perm_list:
                    p, created = SysPermission.objects.get_or_create(
                        code=perm["code"],
                        defaults={
                            "name": perm["name"],
                            "menu": menu,
                            "request_method": perm["method"],
                            "url_path": perm["url_path"],
                        },
                    )
                    status = "新增" if created else "已存在"
                    self.stdout.write(self.style.SUCCESS(f"   {status}权限：{perm['name']} ({perm['code']})"))

        self.stdout.write(self.style.SUCCESS("🎉 菜单与权限初始化完成！"))