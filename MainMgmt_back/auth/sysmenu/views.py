from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .models import SysMenu
from .serializers import SysMenuSerializer
from django.shortcuts import get_object_or_404
from auth.rbac.permissions.drf import CustomPermissionMixin
from django.db import transaction
from rest_framework.decorators import action
from django.db.models import F


class MenuViewSet(viewsets.ModelViewSet):
    """
    视图：对菜单的增删改查
    """
    queryset = SysMenu.objects.all()  # 获取所有菜单
    serializer_class = SysMenuSerializer  # 使用的序列化器
    permission_classes = [CustomPermissionMixin]
    permission_code_map = {
        'create': 'menu:add',
        'update': 'menu:edit',
        'destroy': 'menu:delete',
        'list': 'menu:list',
    }

    @action(
        detail=False,                         # 集合级动作：URL 不带默认 <pk>/
        methods=['put'],                      # 仅允许 PUT
        url_path=r'(?P<parent_id>\d+)/sort'   # 自定义路径：/menus/<parent_id>/sort
    )
    def sort(self, request, parent_id=None):
        """
        批量重排父菜单(parent_id)下的全部子菜单。

        前端传入 `ids`（最终顺序）；若有遗漏，后端会自动把其余子菜单顺延到末尾。
        步骤：
        1. 校验请求体 -> 获取完整子菜单列表
        2. Phase-1：全部 order_num 暂时 +100000（腾出唯一索引空间）
        3. Phase-2：按目标顺序重新编号（间隔 GAP=10），bulk_update 提交
        """

        # ---------- 1. 解析并校验请求体 ----------
        ids = request.data if isinstance(request.data, list) else request.data.get('ids')
        if not isinstance(ids, list) or not ids:
            return Response({'detail': '请求体需为非空数组'}, status=400)

        # ---------- 2. 获取该父菜单下所有子菜单 ----------
        all_menus   = list(SysMenu.objects.filter(parent_id=parent_id))
        id_to_menu  = {menu.id: menu for menu in all_menus}

        # ---------- 3. 生成完整顺序 ----------
        #    ① 先保留前端指定顺序
        #    ② 再把未包含的 ID 依次追加（保持原顺序）
        full_ids = [pk for pk in ids if pk in id_to_menu] + \
                   [pk for pk in id_to_menu if pk not in ids]

        GAP = 10  # 每个序号间隔 10，方便后续插入

        # ---------- 4. 原子事务：两阶段避免唯一索引冲突 ----------
        with transaction.atomic():
            # Phase-1: 先把所有 order_num 挪到安全区（+100000）
            SysMenu.objects.filter(parent_id=parent_id) \
                           .update(order_num=F('order_num') + 100_000)

            # Phase-2: 重新赋值目标序号并批量更新
            for idx, pk in enumerate(full_ids, 1):
                id_to_menu[pk].order_num = idx * GAP

            # bulk_update 一次性提交，batch_size 可根据行数调整
            SysMenu.objects.bulk_update(all_menus, ['order_num'], batch_size=1000)

        # ---------- 5. 返回结果 ----------
        return Response({'detail': '排序成功'}, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """
        创建菜单
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # 保存新菜单
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None, *args, **kwargs):
        """
        更新菜单
        """
        menu = get_object_or_404(SysMenu, pk=pk)
        serializer = self.get_serializer(menu, data=request.data)
        if serializer.is_valid():
            serializer.save()  # 保存更新后的菜单
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None, *args, **kwargs):
        """
        删除菜单
        """
        menu = get_object_or_404(SysMenu, pk=pk)
        menu.delete()  # 删除菜单
        return Response({"message": "Menu deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

    def list(self, request, *args, **kwargs):
        """
        获取所有菜单列表，按照 order_num 进行排序，并返回树形结构
        """
        # 1. 查询所有菜单，并按 order_num 排序
        queryset = self.get_queryset().order_by('order_num')

        # 2. 使用公共方法构建菜单树形结构
        menu_tree = build_menu_tree(queryset)

        # 3. 序列化菜单树结构
        serializer = self.get_serializer(menu_tree, many=True)

        # 4. 返回排序和树形结构后的菜单数据
        return Response(serializer.data)


def build_menu_tree(menus):
    """
    构建菜单树形结构，并按 order_num 对一级菜单及子菜单进行排序
    :param menus: 查询出的所有菜单
    :return: 树形结构的菜单列表
    """
    menu_dict = {}  # 用于保存菜单的字典，以便根据 ID 快速查找父菜单
    for menu in menus:
        menu_dict[menu.id] = menu  # 通过菜单 ID 建立菜单字典

    menu_tree = []  # 最终的菜单树列表
    for menu in menus:
        if menu.parent_id is None or menu.parent_id == 0:  # 顶级菜单条件判断 (None or 0)
            menu_tree.append(menu)
        else:
            # 找到父菜单，并将当前菜单作为子菜单添加到父菜单的 children 列表
            parent_menu = menu_dict.get(menu.parent_id)
            if parent_menu:
                if not hasattr(parent_menu, 'children'):
                    parent_menu.children = []  # 初始化 children 列表
                parent_menu.children.append(menu)

    # 对一级菜单按 order_num 进行排序
    menu_tree = sorted(menu_tree, key=lambda x: x.order_num)

    # 对每个父菜单下的 children 也按 order_num 进行排序
    for menu in menu_tree:
        if hasattr(menu, 'children'):
            menu.children = sorted(menu.children, key=lambda x: x.order_num)

    return menu_tree  # 返回树形结构的菜单
