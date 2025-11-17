<script setup>
import { ref, onMounted, nextTick } from 'vue';
import authHttp from '@/api/authHttp';
import { ElMessage, ElTree, ElMessageBox } from 'element-plus';
import IconInput from '@/components/SvgIcon/iconInput.vue';
import menuPermission from './com/menuPermission.vue';
import { useThemeStore } from '@/stores/theme';
import { useDarkMode } from '@/stores/isDark';
const themeStore = useThemeStore();
const isMoving = ref();
const { isDark } = useDarkMode();

/**
 * 上 / 下 移动菜单节点
 */
const handleMove = async (direction) => {
  /* ---------- 0. 防止重入 ---------- */
  if (isMoving.value) return; // 上一次还在进行中

  /* ---------- 1. 获取当前节点 ---------- */
  const currentData = treeRef.value?.getCurrentNode();
  if (!currentData) {
    ElMessage.error(`请先选择一个菜单进行${direction === 'up' ? '上移' : '下移'}`);
    return;
  }

  // TreeNode 对象，包含 parent、level 等结构信息
  const currentNode = treeRef.value.getNode(currentData.id);
  const parentNode = currentNode.parent; // null ⇒ 根层

  /* ---------- 2. 获取同级节点数组 ---------- */
  // 根层：用 menuTreeData；否则：用 parent.data.children
  const siblings = parentNode && parentNode.level !== 0 ? parentNode.data.children || [] : menuTreeData.value || [];

  if (siblings.length < 2) {
    ElMessage.warning('没有可移动的同级菜单');
    return;
  }

  /* ---------- 3. 按 order_num,id 排序，确保顺序一致 ---------- */
  const ordered = siblings.slice().sort((a, b) => a.order_num - b.order_num || a.id - b.id);

  /* ---------- 4. 计算目标索引并做边界检查 ---------- */
  const index = ordered.findIndex((item) => item.id === currentData.id);
  const targetIndex = direction === 'up' ? index - 1 : index + 1;

  if (targetIndex < 0 || targetIndex >= ordered.length) {
    ElMessage.warning('已经到边界，无法移动');
    return;
  }

  /* ---------- 5. 构造最终 id 顺序 ---------- */
  const newIds = ordered.map((item) => item.id); // 纯 id 数组
  // ES6 解构交换位置
  [newIds[index], newIds[targetIndex]] = [newIds[targetIndex], newIds[index]];

  /* ---------- 6. 调用后端批量排序接口 ---------- */
  const parentId =
    parentNode && parentNode.level !== 0
      ? parentNode.data.id // 子层
      : 0; // 根层约定 0

  isMoving.value = true; // 上锁 + 开启按钮 loading
  try {
    await authHttp.sortMenu(parentId, newIds); // 后端两阶段更新
    ElMessage.success(`菜单${direction === 'up' ? '上移' : '下移'}成功`);

    /* ---------- 7. 刷新树并恢复高亮 ---------- */
    await requestMenu(); // 从后台重新拉数据
    treeRef.value?.setCurrentKey(currentData.id); // 维持选中
  } catch (err) {
    // 尽量提取后端 detail 字段，否则打印 message
    ElMessage.error(`移动失败：`, err);
  } finally {
    isMoving.value = false; // 解锁
  }
};

const menuTreeData = ref([]); // 菜单树数据
const treeRef = ref(null); // 菜单树的引用
const dialogVisible = ref(false);
const dialogMode = ref('add'); // 用来标记当前操作模式：'add', 'edit', 'copy'
const form = ref({});
const formRef = ref(null);
const selectedMenuId = ref(null); // 添加一个ref来存储当前选中的菜单id

// 加载菜单数据
const requestMenu = async () => {
  try {
    const data = await authHttp.getMenu();
    menuTreeData.value = data;
    flatMenus.value = flattenMenuData(data); // 扁平化菜单数据
  } catch (message) {
    ElMessage.error(message);
  }
};

// 新增or编辑——菜单
const showDialog = (row, mode) => {
  if (mode === 'edit') {
    Object.assign(form.value, row); // 将选中行的数据填充到表单中
    dialogMode.value = 'edit';
    dialogVisible.value = true;
  } else if (mode === 'add') {
    Object.keys(form.value).forEach((key) => {
      form.value[key] = '';
    });
    dialogVisible.value = true;
    dialogMode.value = 'add';
  }
};
let selectedNode;
//菜单管理
// const requestManagerMenu = async () => {
//   formRef.value.validate(async (valid) => {
//     if (valid) {
//       const data = { ...form.value };
//       try {
//         let newId;
//         if (dialogMode.value === 'add') {
//           await authHttp.addMenu(data);
//           ElMessage.success('添加成功');
//         } else if (dialogMode.value === 'edit') {
//           await authHttp.updateMenu(form.value.id, data);
//           ElMessage.success('修改成功');
//           newId = form.value.id;
//         }
//         await requestMenu();
//         nextTick(() => {
//           if (selectedMenuId.value) {
//             treeRef.value?.setCurrentKey(selectedMenuId.value); // 重新选中
//           }
//         });
//         treeRef.value?.setCurrentKey(newId); // 重新选中：根层或者子层都通用
//         dialogVisible.value = false;
//       } catch (message) {
//         ElMessage.error(message);
//       }
//     } else {
//       ElMessage.error('按要求填写有效的信息');
//     }
//   });
// };
const requestManagerMenu = async () => {
  formRef.value.validate(async (valid) => {
    if (!valid) {
      ElMessage.error('请按要求填写有效的信息');
      return;
    }

    const data = { ...form.value };
    
    // **调试日志**
    console.log('准备提交菜单数据:', data);
    
    try {
      let response;
      
      if (dialogMode.value === 'edit') {
        response = await authHttp.updateMenu(form.value.id, data);
        ElMessage.success('修改成功');
      } else if (dialogMode.value === 'add') {
        response = await authHttp.addMenu(data);
        ElMessage.success('添加成功');
      }
      
      // **关键修复：检查响应是否包含错误**
      if (response && (response.statusCode === 400 || response.status === 400 || response.detail)) {
        // 手动抛出错误，让 catch 捕获
        throw response;
      }
      
      await requestMenu();
      nextTick(() => {
        treeRef.value?.setCurrentKey(selectedMenuId.value);
      });
      dialogVisible.value = false;
      
    } catch (error) {
      // **核心：提取详细错误信息**
      console.error('菜单操作失败:', error);
      
      let errorMsg = '操作失败';
      
      // Django REST framework 格式
      if (error?.detail) {
        errorMsg = error.detail;
      } 
      // Axios 错误格式
      else if (error?.response?.data?.detail) {
        errorMsg = error.response.data.detail;
      }
      // 字段验证错误
      else if (error?.response?.data) {
        const responseData = error.response.data;
        const fieldErrors = Object.entries(responseData)
          .map(([key, value]) => {
            if (Array.isArray(value)) return `${key}: ${value.join(', ')}`;
            return `${key}: ${value}`;
          })
          .join('; ');
        errorMsg = fieldErrors || errorMsg;
      }
      // 兜底
      else if (typeof error === 'string') {
        errorMsg = error;
      } else {
        errorMsg = JSON.stringify(error);
      }
      
      // **确保错误消息不为空**
      if (!errorMsg || errorMsg === '{}') {
        errorMsg = '操作失败：服务器返回 400 错误（数据验证失败）';
      }
      
      ElMessage.error({
        message: errorMsg,
        duration: 5000,
        showClose: true
      });
    }
  });
};

// 修改菜单
const handleEdit = () => {
  selectedNode = treeRef.value.getCurrentNode(); // 获取当前选中的树节点

  if (selectedNode) {
    showDialog(selectedNode, 'edit'); // 调用 showDialog 显示编辑框
  } else {
    ElMessage.error('请先选择一个菜单进行编辑');
  }
};

//删除菜单
const deleteMenu = async (row) => {
  try {
    await authHttp.deleteMenu(row.id);
    ElMessage.success('删除成功');
    requestMenu();
  } catch (message) {
    ElMessage.error(message);
  }
};

//删除菜单
const handleDelete = () => {
  let selectedNode = treeRef.value.getCurrentNode(); // 获取当前选中的树节点
  if (!selectedNode) {
    ElMessage.error('请先选择一个菜单进行删除');
    return;
  }

  // 弹出确认提示框
  ElMessageBox.confirm(`确认删除菜单 "${selectedNode.text}" 吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
    .then(async () => {
      await deleteMenu(selectedNode); // 调用 deleteMenu 执行删除操作
    })
    .catch(() => {
      ElMessage.info('已取消删除');
    });
};

// 扁平化菜单数据，用于展示父菜单选择
const flatMenus = ref([]);

const flattenMenuData = (menus, level = 0) => {
  const result = [];
  menus.forEach((menu) => {
    // 仅处理 menu_type === 'M' 的目录菜单
    if (menu.menu_type === 'M') {
      result.push({
        id: menu.id,
        text: menu.text,
        level: level,
        textWithLevel: `${'--'.repeat(level)} ${menu.text}` // 用 '--' 表示缩进层级
      });
    }

    // 递归处理子菜单
    if (menu.children && menu.children.length > 0) {
      result.push(...flattenMenuData(menu.children, level + 1));
    }
  });
  return result;
};

// 调用请求权限数据的方法，并传递选中节点的 id
const handleNodeClick = (node) => {
  selectedMenuId.value = node.id;
};

const handleTopMenuClick = () => {
  selectedMenuId.value = null;
};

onMounted(() => {
  requestMenu(); // 初始化加载菜单
});
</script>

<template>
  <div style="display: flex">
    <!-- 菜单列表 -->
    <div style="width: 25%; margin-top: 0.5%; margin-right: 0.5%">
      <el-card v-permission="'menu:list'" class="menu-card">
        <div class="menu-item" style="margin-left: 1%">
          <SvgIcon style="margin-right: 1%" name="menu"
            :filter="themeStore.theme === 'dark' ? 'grayscale(1) brightness(2)' : ''" />
          <el-text class="menutext" @click="handleTopMenuClick" style="cursor: pointer">菜单列表</el-text>
        </div>
        <div style="height: 75vh; overflow: auto">
          <el-tree ref="treeRef" :data="menuTreeData" :props="{ children: 'children', label: 'text' }" node-key="id"
            highlight-current node-click @node-click="handleNodeClick">
            <template #default="{ data }">
              <div class="menu-item">
                <el-icon style="margin-right: 5%">
                  <SvgIcon :name="data.icon"
                    :filter="themeStore.theme === 'dark' ? 'grayscale(1) brightness(2)' : ''" />
                </el-icon>
                <el-text>{{ data.text }}</el-text>
              </div>
            </template>
          </el-tree>
        </div>

        <el-divider style="position: absolute; bottom: 5%" />
        <!-- 菜单操作按钮 -->
        <div class="operation-buttons">
          <el-tooltip effect="dark" content="添加菜单" placement="top">
            <el-icon v-permission="'menu:add'" class="custom-icon" @click="showDialog('', 'add')">
              <Plus />
            </el-icon>
          </el-tooltip>

          <el-tooltip effect="dark" content="编辑菜单" placement="top">
            <el-icon v-permission="'menu:edit'" class="custom-icon" @click="handleEdit">
              <Edit />
            </el-icon>
          </el-tooltip>

          <el-tooltip effect="dark" content="菜单上移" placement="top">
            <el-icon 
                v-permission="'menu:edit'"
                class="custom-icon" :class="{ 'is-disabled': isMoving }" 
                @click="!isMoving && handleMove('up')"
            >
              <ArrowUp />
            </el-icon>
          </el-tooltip>

          <el-tooltip  effect="dark" content="菜单下移" placement="top">
            <el-icon 
                v-permission="'menu:edit'"
                class="custom-icon" :class="{ 'is-disabled': isMoving }" 
                @click="!isMoving && handleMove('down')"
            >
              <ArrowDown />
            </el-icon>
          </el-tooltip>

          <el-tooltip effect="dark" content="删除菜单" placement="top">
            <el-icon v-permission="'menu:delete'" class="custom-icon" @click="handleDelete">
              <Delete />
            </el-icon>
          </el-tooltip>
        </div>
      </el-card>
    </div>
    <!-- 权限表 -->
    <menuPermission :menuId="selectedMenuId" />

    <!-- 菜单对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogMode === 'edit' ? '修改菜单' : '新增菜单'" width="25%"
      style="padding-right: 3%">
      <el-form ref="formRef" :model="form" label-width="100px">
        <el-form-item label="菜单标识" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="菜单名称" prop="text">
          <el-input v-model="form.text" />
        </el-form-item>
        <el-form-item label="图标" prop="icon">
          <IconInput v-model="form.icon" />
        </el-form-item>
        <el-form-item label="父菜单" prop="parent_id">
          <el-select v-model="form.parent_id" placeholder="请选择父菜单" style="width: 100%">
            <!-- 添加顶层菜单选项 -->
            <el-option label="无" :value="0"></el-option>
            <!-- 显示所有菜单，包括一级、二级、三级菜单 -->
            <el-option v-for="menu in flatMenus" :key="menu.id" :label="menu.textWithLevel"
              :value="menu.id"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="显示顺序" prop="order_num">
          <el-input v-model="form.order_num" type="number" />
        </el-form-item>
        <el-form-item label="路由地址" prop="path">
          <el-input v-model="form.path" />
        </el-form-item>
        <el-form-item label="菜单类型" prop="menu_type">
          <el-select v-model="form.menu_type" placeholder="请选择菜单类型" style="width: 100%">
            <el-option label="菜单" value="C"></el-option>
            <el-option label="目录" value="M"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button color="#626aef" :dark="isDark" plain @click="dialogVisible = false">取消</el-button>
        <el-button color="#626aef" :dark="isDark" plain @click="requestManagerMenu">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.menu-card {
  height: 90vh;
  display: flex;
  flex-direction: column;
  position: relative;
  /* 让子元素使用绝对定位 */
}

.operation-buttons {
  width: 90%;
  display: flex;
  justify-content: space-between;
  position: absolute;
  /* 绝对定位 */
  bottom: 2%;
}

.el-divider--horizontal {
  width: 90%;
}

.menu-item {
  display: flex;
  align-items: center;
  /* 垂直居中 */
  justify-content: flex-start;
  /* 水平从左到右排列 */
  padding: 5px 0;
  /* 可根据需要调整间距 */
}

.el-tree {
  --el-tree-node-content-height: 32px;
}

.menutext {
  font-weight: bold;
}

.custom-icon {
  font-size: 20px;
  padding: 10px;
  /* 增加内边距，保持正方形外观 */
  border-radius: 4px;
  /* 添加圆角，提升柔和感 */
  display: inline-flex;
  justify-content: center;
  align-items: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  /* 添加更细致的阴影 */
  transition: all 0.3s ease;
  /* 平滑过渡效果 */
  cursor: pointer;
  /* 鼠标悬停时显示为指针，提升交互感 */
}

.custom-icon:hover {
  background-color: #626aef;
  /* 悬停时改变背景色 */
  color: #fff;
  /* 改变图标颜色 */
  transform: scale(1.1);
  /* 悬停时放大图标 */
  border-color: #626aef;
  /* 悬停时边框颜色也改变 */
}

.custom-icon:active {
  transform: scale(1.05);
  /* 按下时稍微缩小 */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  /* 按下时加深阴影 */
}

.is-disabled {
  opacity: 0.5;
  /* pointer-events: none; */
  cursor: not-allowed;
}
</style>
