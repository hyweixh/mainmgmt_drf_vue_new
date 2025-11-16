<script setup>
import authHttp from '@/api/authHttp';
import { ref, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import timeFormatter from '@/utils/timeFormatter';
import OperationButton from '@/components/OperationButton.vue';
import { useThemeStore } from '@/stores/theme';
const themeStore = useThemeStore();

import { useDarkMode } from '@/stores/isDark';
const { isDark } = useDarkMode();

const goBack = () => {
  drawerVisible.value = false;
};

const dialogVisible = ref(false); // 控制新增对话框的可见性
const dialogMode = ref('add'); // 用来标记当前操作模式：'add', 'edit', 'copy'
const tableData = ref([]); //角色表格
const tableData_permission = ref([]); //角色表格

const formRef = ref(null);
const form = ref({});
const menuTree = ref([]); // 菜单树数据
const drawerVisible = ref(false); // 控制抽屉可见性
const selectedRole = ref(null); // 保存当前选中的角色
const treeRef = ref(null); // 保存el-tree组件实例，用于获取选中的节点
const selectedMenuId = ref(null); // 添加一个ref来存储当前选中的菜单id
const selectedPermissions = ref([]); // 用于存储选中的权限ID

// 显示新增或编辑vm对话框并重置表单
const showDialog = (row, mode) => {
  if (mode === 'edit') {
    Object.assign(form.value, row); // 将选中行的数据填充到表单中
    dialogMode.value = 'edit';
  } else {
    Object.keys(form.value).forEach((key) => {
      if (key !== 'status') {
        form.value[key] = ''; // 重置除了 status 的其他字段
      }
    });
    dialogMode.value = 'add';
  }
  dialogVisible.value = true;
};

const requestRole = async () => {
  try {
    const data = await authHttp.getRoleInfo();
    tableData.value = data.results;
  } catch (message) {
    ElMessage.error(message);
  }
};

// 请求菜单树
const requestMenu = async () => {
  try {
    const data = await authHttp.getMenu();
    menuTree.value = data;
  } catch (message) {
    ElMessage.error(message);
  }
};

//请求权限数据
const requesPermission = async (menu_id) => {
  try {
    const data = await authHttp.getPermission(menu_id, 1, 100);
    tableData_permission.value = data.results;
  } catch (message) {
    ElMessage.error(message);
  }
};

// 调用请求权限数据的方法，并传递选中节点的 id
const handleNodeClick = (node) => {
  selectedMenuId.value = node.id;
  requesPermission(node.id);
};

// 分配菜单
const assign_menu = async () => {
  try {
    // 获取选中的菜单ID
    const checkedKeys = treeRef.value.getCheckedKeys(); // 获取选中菜单节点的ID列表

    const Menudata = {
      role_id: selectedRole.value.id, // 当前选中的角色ID
      menu_ids: checkedKeys // 选中的菜单ID数组，直接传递ID数组
    };

    const rolePermissionData = {
      role: selectedRole.value.id,
      permissions: selectedPermissions.value
    };

    await authHttp.assignMenu(Menudata);
    await authHttp.addRolePermission(rolePermissionData);
    ElMessage.success('权限分配成功');
    drawerVisible.value = false; // 成功后关闭抽屉
  } catch (message) {
    ElMessage.error(message);
  }
};

// 点击分配权限按钮时，打开抽屉并保存当前选中的角色
const openAssignMenuDrawer = async (row) => {
  requestMenu();
  drawerVisible.value = true; // 打开抽屉
  selectedRole.value = row; // 保存当前选中的角色
  try {
    // 获取当前角色已有的权限菜单ID数组
    const assignedMenuIds = await authHttp.getRoleMenu(row.id);
    // 提取所有的菜单 ID
    const checkedKeys = assignedMenuIds.map((menu) => menu.id);
    console.log(checkedKeys);
    // 自动勾选菜单节点
    treeRef.value.setCheckedKeys(checkedKeys);

    const rolePermissions = await authHttp.getRolePermission(row.id); // 请求角色已分配的权限

    selectedPermissions.value = rolePermissions.map((item) => item.permission); //勾选按钮
  } catch (message) {
    ElMessage.error(message);
  }
};

onMounted(() => {
  requestRole();
});

const requestManagerRole = async () => {
  formRef.value.validate(async (valid) => {
    if (valid) {
      const data = {
        name: form.value.name,
        code: form.value.code,
        remark: form.value.remark
      };
      try {
        if (dialogMode.value === 'add') {
          await authHttp.addRole(data);
          ElMessage.success('添加成功');
        } else if (dialogMode.value === 'edit') {
          await authHttp.updateRole(form.value.id, data);
          ElMessage.success('修改成功');
        }
        requestRole();
        dialogVisible.value = false;
      } catch (message) {
        ElMessage.error(message);
      }
    } else {
      ElMessage.error('按要求填写有效的信息');
    }
  });
};

//删除
const onDelete = async (row) => {
  try {
    await authHttp.DeleteRole(row.id);
    ElMessage.success('删除成功');
    requestRole();
  } catch (message) {
    ElMessage.error(message);
  }
};

const rules = ref({
  name: [{ required: true, message: '角色名称不能为空', trigger: 'blur' }],
  code: [{ required: true, message: '权限标识不能为空', trigger: 'blur' }]
});
</script>

<template>
  <div>
    <!-- 表格数据 -->
    <el-card>
      <el-button color="#626aef" :dark="isDark" icon="Plus" @click="showDialog(false)">新增角色</el-button>
    </el-card>
    <div :class="['table-container', themeStore.theme]">
      <el-table :data="tableData" style="width: 100%">
        <el-table-column type="index" label="序号" width="100" align="center" />
        <el-table-column prop="name" label="角色名称" align="center" />
        <el-table-column prop="code" label="权限标识" align="center" />
        <el-table-column prop="create_time" label="创建时间" align="center" />
        <el-table-column label="更新时间" align="center">
          <template v-slot="scope">
            {{ timeFormatter.stringFromDateTime(scope.row.update_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" align="center" />
        <el-table-column label="权限设置" align="center">
          <template #default="{ row }">
            <el-button color="#626aef" plain :dark="isDark" size="small" icon="Menu" @click="openAssignMenuDrawer(row)">菜单权限</el-button>
          </template>
        </el-table-column>

        <el-table-column prop="action" label="操作" width="150" fixed="right" align="center">
          <template #default="{ row }">
            <div style="display: flex; justify-content: space-around">
              <operation-button type="edit" @click="showDialog(row, 'edit')" />
              <operation-button type="delete" @click="onDelete(row)" />
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogMode === 'edit' ? '修改角色' : '新增角色'" width="25%" style="padding-right: 3%">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>

        <el-form-item label="权限标识" prop="code">
          <el-input v-model="form.code" />
        </el-form-item>

        <el-form-item label="备注">
          <el-input v-model="form.remark" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button color="#626aef" plain :dark="isDark" @click="dialogVisible = false">取消</el-button>
        <el-button color="#626aef" plain :dark="isDark" type="primary" @click="requestManagerRole">确认</el-button>
      </template>
    </el-dialog>

    <!-- 抽屉组件 -->
    <el-drawer v-model="drawerVisible" size="45%">
      <div :class="['drawer-header-container-role', themeStore.theme]">
        <div style="display: flex; align-items: center">
          <el-page-header @back="goBack" content="菜单权限" class="section-title" />
          <div class="role-info">
            <el-text class="label-text">当前授权角色</el-text>
            <el-tag :class="['primary-tag', themeStore.theme]">
              {{ selectedRole.name }}
            </el-tag>
          </div>
        </div>
        <el-button icon="Close" class="icon-copy" @click="goBack" />
      </div>

      <!-- 主内容区域 -->
      <div :class="['drawer-content', themeStore.theme]">
        <!-- 菜单树区域 -->
        <div class="MenuAndPermission-section">
          <div class="section-header">
            <el-icon class="section-icon"><FolderOpened /></el-icon>
            <span class="section-title">菜单结构</span>
          </div>
          <div class="tree-container">
            <el-tree
              ref="treeRef"
              :data="menuTree"
              show-checkbox
              node-key="id"
              highlight-current
              default-expand-all
              :props="{ label: 'text', children: 'children' }"
              check-strictly
              @node-click="handleNodeClick"
              class="menu-tree"
            />
          </div>
        </div>

        <!-- 权限区域 -->
        <div class="MenuAndPermission-section">
          <div class="section-header">
            <el-icon class="section-icon"><Key /></el-icon>
            <span class="section-title">角色列表</span>
            <el-text class="permission-count" v-if="tableData_permission.length">({{ selectedPermissions.length }}/{{ tableData_permission.length }})</el-text>
          </div>
          <div class="tree-container">
            <el-empty v-if="!tableData_permission.length" description="请先选择菜单查看权限" :image-size="200" />
            <el-checkbox-group v-else v-model="selectedPermissions" class="permission-group">
              <el-checkbox v-for="permission in tableData_permission" :key="permission.id" :value="permission.id" class="permission-item">
                <el-text style="font-weight: 400">{{ permission.name }}</el-text>
              </el-checkbox>
            </el-checkbox-group>
          </div>
        </div>
      </div>

      <!-- 分配按钮 -->
      <div style="text-align: center; margin-top: 10px">
        <el-button color="#626aef" plain :dark="isDark" @click="assign_menu">确认分配</el-button>
        <el-button color="#626aef" plain :dark="isDark" @click="drawerVisible = false">取消</el-button>
      </div>
    </el-drawer>
  </div>
</template>

<style scoped>
.label-text{
  color: #909399;
  font-weight: 500;
}

.role-info {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 主内容 */
.drawer-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  height: 86vh;
}

.drawer-content.light {
  background: #fafbfc;
  border-radius: 8px;
  border: 1px solid #e1e8ed;
}

.drawer-content.dark {
  background: #1a1a1a;
  border-radius: 8px;
  border: 1px solid #333;
}

/* 分割线 */
.drawer-content::after {
  content: '';
  position: absolute;
  left: 50%;
  top: 20px;
  bottom: 20px;
  width: 1px;
  background: linear-gradient(to bottom, transparent, #626aef, transparent);
  transform: translateX(-50%);
}

/* 菜单树区域 */
.MenuAndPermission-section {
  padding: 20px;
  display: flex;
  flex-direction: column;
  height: 80vh;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 2px solid #626aef;
}

.section-icon {
  color: #626aef;
  font-size: 16px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.tree-container {
  flex: 1;
  overflow-y: auto;
  padding-right: 8px;
}

/* 树结构 */
.menu-tree :deep(.el-tree-node__content) {
  height: 36px;
  border-radius: 6px;
  margin-bottom: 4px;
  transition: all 0.2s;
}

/* 树结构选中颜色 */
.menu-tree :deep(.el-tree-node__content:hover) {
  background-color: var(--el-color-primary-light-9);
}

/* 权限区域 */
.permission-count {
  color: #626aef;
  font-size: 12px;
  font-weight: 500;
}

.permission-group {
  display: flex;
  flex-direction: column;
}

.permission-item {
  margin: 0;
  padding: 0px 12px;
  border-radius: 6px;
  margin-bottom: 4px;
  height: 36px;
  transition: all 0.2s;
}

.permission-item:hover {
  background: var(--el-color-primary-light-9);
  transform: translateX(5px);
}

/* 底部按钮 */
.drawer-footer {
  display: flex;
  justify-content: center;
  gap: 12px;
  padding: 16px 0;
  background: var(--el-bg-color);
}

/* 滚动条样式 */
.tree-container::-webkit-scrollbar {
  width: 3px;
}

.tree-container::-webkit-scrollbar-thumb {
  background: #626aef;
  border-radius: 3px;
}
</style>
