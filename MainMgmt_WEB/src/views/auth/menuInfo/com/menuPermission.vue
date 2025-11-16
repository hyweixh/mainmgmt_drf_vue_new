<script setup>
import { ref, watch, onMounted, reactive } from 'vue';
import authHttp from '@/api/authHttp';
import { ElMessage } from 'element-plus';
import OperationButton from '@/components/OperationButton.vue';
import Pagination from '@/components/Pagination.vue';
import { downloadFile } from '@/utils/downloadUtils';
import { useThemeStore } from '@/stores/theme';
const themeStore = useThemeStore();

import { useDarkMode  } from '@/stores/isDark'; 
const { isDark } = useDarkMode();

// 修改 props 的名称为 menuId
const props = defineProps({
  menuId: {
    type: [Number, null],
    required: true,
    default: null
  }
});

const dialogVisible_permission = ref(false);
const dialogMode_permission = ref('add');
const form_permission = ref({});
const formRef_permission = ref(null);
const tableData = ref([]);

// 新增or编辑——权限
const showDialog_permission = (row, mode) => {
  if (props.menuId === null) {
    ElMessage.warning('请先选择菜单');
  } else {
    if (mode === 'edit') {
      Object.assign(form_permission.value, row);
      dialogMode_permission.value = 'edit';
    } else if (mode === 'copy') {
      Object.assign(form_permission.value, row);
      dialogMode_permission.value = 'copy';
    } else if (mode === 'add') {
      Object.keys(form_permission.value).forEach((key) => {
        form_permission.value[key] = '';
        dialogMode_permission.value = 'add';
      });
    }
    dialogVisible_permission.value = true;
  }
};

//删除权限
const deletePermission = async (row) => {
  try {
    await authHttp.delPermission(row.id);
    ElMessage.success('删除成功');
    // 检查删除后是否需要调整页码
    const remainingItems = tableData.value.length - 1; // 当前页剩余条目数（已删除1条）

    // 如果没有剩余数据且页码大于1，自动减一页
    if (remainingItems === 0 && pagination.page > 1) {
      pagination.page -= 1;
    }
    requesPermission(pagination.page, page_size.value);
  } catch (message) {
    ElMessage.error(message);
  }
};

//请求权限数据
const requesPermission = async (page, size) => {
  try {
    const data = await authHttp.getPermission(props.menuId, page, size);
    tableData.value = data.results;

    pagination.total = data.count;
    pagination.page = page;
  } catch (message) {
    ElMessage.error(message);
  }
};

//权限管理
const requestManagerPermission = async () => {
  formRef_permission.value.validate(async (valid) => {
    if (valid) {
      const data = {
        name: form_permission.value.name,
        code: form_permission.value.code,
        remark: form_permission.value.remark,
        menu: props.menuId,
        request_method: form_permission.value.request_method,
        url_path: form_permission.value.url_path
      };
      try {
        if (dialogMode_permission.value === 'add' || dialogMode_permission.value === 'copy') {
          await authHttp.addPermission(data);
          ElMessage.success('添加成功');
        } else if (dialogMode_permission.value === 'edit') {
          await authHttp.updatePermission(form_permission.value.id, data);
          ElMessage.success('修改成功');
        }
        requesPermission(pagination.page, page_size.value);
        console.log(pagination.page, page_size.value);
        dialogVisible_permission.value = false;
      } catch (message) {
        ElMessage.error(message);
      }
    } else {
      ElMessage.error('按要求填写有效的信息');
    }
  });
};

watch(
  () => props.menuId,
  (newMenuId) => {
    // 每次切换菜单时重置分页到第一页
    if (newMenuId !== null) {
      pagination.page = 1; // 切换菜单时重新请求第一页数据
    }
    requesPermission(pagination.page, page_size.value);
  }
);

onMounted(() => {
  requesPermission(pagination.page, page_size.value);
});

let pagination = reactive({
  total: 0, // 分页总数
  page: 1 // 当前页数
});

let page_size = ref(15);

// 更新页码
const updatePage = (newPage) => {
  pagination.page = newPage;
  requesPermission(newPage, page_size.value);
};

// 更新条目数
const updatePageSize = (newPageSize) => {
  page_size.value = newPageSize;
  requesPermission(pagination.page, newPageSize);
};

//导出
const exportPermissions = async () => {
  try {
    const response = await authHttp.permissionExport({
      responseType: 'blob' // 设置响应类型为文件流
    });
    downloadFile(response.data, 'permissions.xlsx','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
  } catch (message) {
    ElMessage.error(message);
  }
};

const getTagType = (method) => {
  switch (method) {
    case 'GET':
      return 'success';
    case 'POST':
      return 'warning';
    case 'DELETE':
      return 'danger';
  }
};
</script>

<template>
  <div :class="['table-container', themeStore.theme]" style="width: 75%; margin-top: 0.7%;   padding: 0 10px; height: 89.8vh">
    <div style="display: flex; justify-content: space-between; margin: 1% 0%">
      <el-button v-permission="'permission:add'" :dark="isDark" icon="Plus" color="#626aef" @click="showDialog_permission(false, 'add')">添加</el-button>
      <el-button v-permission="'permission:export'" :dark="isDark" icon="download" color="#626aef" @click="exportPermissions">导出</el-button>
    </div>
    <el-table ref="tableRef" :data="tableData" border style="height: 78vh" >
      <el-table-column type="index" label="序号" align="center" width="80" />
      <el-table-column prop="name" label="权限名称" align="center" />
      <el-table-column prop="code" label="权限标识" align="center" />
      <el-table-column label="请求方式" align="center" width="120">
        <template #default="{ row }">
          <el-tag :type="getTagType(row.request_method)" effect="dark" :class="{ 'primary-tag': row.request_method === 'PUT' }" size="small">
            {{ row.request_method }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="url_path" label="接口地址" align="center" width="300">
        <template #default="{ row }">
          <el-tag :type="getTagType(row.request_method)" effect="plain" :class="{ 'primary-tag': row.url_path === 'PUT' }" size="small">
            {{ row.url_path }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="remark" label="备注" align="center" />
      <el-table-column v-permission="'permission:edit'" prop="action" label="操作" width="150" align="center">
        <template #default="{ row }">
          <div style="display: flex; justify-content: space-around">
            <operation-button v-permission="'permission:edit' "
                type="edit" @click="showDialog_permission(row, 'edit')" />
            <operation-button v-permission="'permission:copy'"
                type="copy" @click="showDialog_permission(row, 'copy')" />
            <operation-button v-permission="'permission:delete'"
                type="delete" @click="deletePermission(row)" />
          </div>
        </template>
      </el-table-column>
    </el-table>
    <!-- 分页 -->
    <Pagination :total="pagination.total" :page="pagination.page" @update:page="updatePage" @update:pageSize="updatePageSize" />
  </div>

  <!-- 权限对话框 -->
  <el-dialog v-model="dialogVisible_permission" :title="dialogMode_permission === 'edit' ? '修改权限' : '新增权限'" width="25%" style="padding-right: 3%">
    <el-form ref="formRef_permission" :model="form_permission" label-width="100px">
      <el-form-item label="权限名称" prop="name">
        <el-input v-model="form_permission.name" />
      </el-form-item>
      <el-form-item label="菜单标识" prop="code">
        <el-input v-model="form_permission.code" />
      </el-form-item>
      <el-form-item label="请求方式" prop="request_method">
        <el-select v-model="form_permission.request_method" placeholder="请选择请求方式" style="width: 100%;">
          <el-option label="GET" value="GET"></el-option>
          <el-option label="POST" value="POST"></el-option>
          <el-option label="PUT" value="PUT"></el-option>
          <el-option label="DELETE" value="DELETE"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="接口地址" prop="url_path">
        <el-input v-model="form_permission.url_path" />
      </el-form-item>
      <el-form-item label="备注">
        <el-input v-model="form_permission.remark" type="text" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button :dark="isDark" color="#626aef" plain @click="dialogVisible_permission = false">取消</el-button>
      <el-button :dark="isDark" color="#626aef" plain @click="requestManagerPermission">确认</el-button>
    </template>
  </el-dialog>
</template>
