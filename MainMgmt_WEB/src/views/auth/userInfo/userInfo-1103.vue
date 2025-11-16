<template>
  <div>
    <!-- 1. 顶部筛选栏：用户搜索 + 新增按钮 -->
    <el-card>
      <!-- 用户名模糊搜索框 -->
      <el-input
        placeholder="请输入用户名..."
        v-model="queryForm.username"
        clearable
        style="width: 15%"
      ></el-input>

      <!-- 搜索按钮：触发用户列表查询 -->
      <el-button
        color="#626aef"
        icon="Search"
        @click="requestUser"
        style="margin-left: 0.5%"
        >搜索</el-button
      >

      <!-- 新增用户按钮：权限控制（需user:add权限） -->
      <el-button
        v-if="hasPerm('user:add')"
        color="#626aef"
        icon="Plus"
        @click="handleAdd"
      >
        新增
      </el-button>
    </el-card> 

    <!-- 2. 表格容器：动态列渲染 + 主题适配 -->
    <div :class="['table-container', themeStore.theme]">
      <el-table 
        :data="tableData" 
        style="width: 100%"
        
        :key="tableRenderKey" 
      >
        <!-- 动态列循环：用template包裹v-for明确作用域 -->       
        <template v-for="(col, index) in columns" :key="`col_${index}_${col.label}_${col.width || ''}`">
           <!-- 列权限控制：无perm则显示，有perm需校验 -->
          <el-table-column            
            v-if="hasColumnPerm(col.perm)" 
            :label="col.label"       
            :width="col.width"         
            :align="col.align || 'center'" 
            :fixed="col.fixed" 
          >
            <!-- 列内容作用域插槽：根据列类型渲染不同内容 -->
            <template #default="scope">
              <!-- 头像列：渲染用户头像 -->
              <template v-if="col.prop === 'avatar'">
                <img
                  :src="imageUrl + scope.row.avatar"
                  alt="头像"
                  width="35"
                  height="35"
                />
              </template>

              <!-- 角色列：循环渲染用户关联的角色标签 -->
              <template v-else-if="col.prop === 'roles'">
                <el-tag
                  v-for="role in scope.row.roles"
                  :key="role.id"
                  :class="['primary-tag', themeStore.theme]"
                  effect="plain"
                >
                  {{ role.name }}
                </el-tag>
              </template>

              <!-- 状态列：根据用户状态显示不同标签 -->
              <template v-else-if="col.prop === 'status'">
                <el-tag v-if="scope.row.status === 1" type="success">正常</el-tag>
                <el-tag v-else-if="scope.row.status === 2" type="warning">未激活</el-tag>
                <el-tag v-else-if="scope.row.status === 3" type="danger">锁定</el-tag>
              </template>

              <!-- 最后登录时间列：格式化时间戳 -->
              <template v-else-if="col.prop === 'last_login'">
                {{ timeFormatter.stringFromDateTime(scope.row.last_login) }}
              </template>

              <!-- 重置密码列：按钮触发密码重置 -->
              <template v-else-if="col.prop === 'resetPwd'">
                <el-button
                  type="primary"
                  @click="handleReset(scope.row)"
                >
                  重置密码
                </el-button>
              </template>

              <!-- 操作列：编辑/删除按钮（分别做权限控制） -->
              <template v-else-if="col.prop === 'action'">
                <div style="display: flex; justify-content: space-around;">
                  <operation-button
                    v-if="hasPerm('user:edit')"
                    type="edit"
                    @click="handleEdit(scope.row)"
                  />
                  <operation-button
                    v-if="hasPerm('user:delete')"
                    type="delete"
                    @click="handleDelete(scope.row)"
                  /> 
                </div>
              </template>

              <!-- 常规文本列：直接渲染字段值 -->
              <template v-else>
                {{ scope.row[col.prop] }}
              </template>
            </template>
          </el-table-column>
        </template>
      </el-table>
    </div>

    <!-- 3. 新增 / 编辑 用户对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'edit' ? '修改用户' : '新增用户'"
      width="25%"
      style="padding-right: 3%"
    >
      <!-- 表单校验：结合rules做字段验证 -->
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" />
          <el-alert
            title="默认初始密码：123456"
            :closable="false"
            style="line-height: 10px"
            type="success"
          ></el-alert>
        </el-form-item>
        <el-form-item label="姓名" prop="realname">
          <el-input v-model="form.realname" />
        </el-form-item>
        <el-form-item label="手机号" prop="telephone">
          <el-input v-model="form.telephone" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio :value="1">正常</el-radio>
            <el-radio :value="3">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="角色">
          <el-select style="width: 100%" v-model="form.roles" multiple>
            <el-option
              v-for="i in Roles"
              :key="i.id"
              :label="i.name"
              :value="i.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button color="#626aef" plain @click="dialogVisible = false">取消</el-button>
        <el-button color="#626aef" plain @click="requestManagerUser">确认</el-button>
      </template>
    </el-dialog>

    <!-- 4. 重置密码对话框 -->
    <el-dialog
      v-model="resetPwdDialogVisible"
      title="重置密码"
      width="25%"
    >
      <el-form ref="resetPwdFormRef" :model="resetPwdForm" label-width="100px">
        <el-form-item label="用户名" disabled>
          <el-input v-model="cur_user.username" />
        </el-form-item>
        <el-form-item
          label="新密码"
          prop="pwd1"
          :rules="[{ required: true, message: '请输入新密码' }]"
        >
          <el-input v-model="resetPwdForm.pwd1" type="password" />
        </el-form-item>
        <el-form-item
          label="确认密码"
          prop="pwd2"
          :rules="[{ required: true, message: '请再次输入新密码' }]"
        >
          <el-input v-model="resetPwdForm.pwd2" type="password" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button color="#626aef" plain @click="resetPwdDialogVisible = false">取消</el-button>
        <el-button color="#626aef" @click="submitResetPassword">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
/* -------------------------------------------------
 * 0. 引入依赖：接口、Vue API、UI组件、工具函数等
 * ------------------------------------------------- */
import authHttp from '@/api/authHttp';          // 封装的axios实例（带token拦截）
import { ref, reactive, onMounted, watch } from 'vue'; // Vue响应式API
import { ElMessage } from 'element-plus';       // 消息提示组件
import timeFormatter from '@/utils/timeFormatter'; // 时间格式化工具
import OperationButton from '@/components/OperationButton.vue'; // 自定义操作按钮组件
import { useThemeStore } from '@/stores/theme'; // Pinia主题状态管理
import { getPerms } from '@/utils/permission';  // 权限工具函数

/* -------------------------------------------------
 * 1. 响应式数据定义：页面状态、表单、表格数据等
 * ------------------------------------------------- */
const themeStore = useThemeStore();            // 主题状态（深色/浅色）
let handleIndex = 0;                           // 行操作索引（预留）
const cur_user = ref();                        // 重置密码时的当前用户
const resetPwdDialogVisible = ref(false);      // 重置密码弹窗显隐
const resetPwdForm = reactive({ pwd1: '', pwd2: '' }); // 重置密码表单
const imageUrl = import.meta.env.VITE_BASE_URL + '/media/userAvatar/'; // 头像资源路径
const dialogVisible = ref(false);              // 新增/编辑弹窗显隐
const dialogMode = ref('add');                 // 弹窗模式：add/edit
const tableData = ref([]);                     // 表格数据源
const queryForm = ref({});                     // 搜索条件
const formRef = ref(null);                     // 新增/编辑表单引用（用于校验）
const form = ref({ status: 1 });               // 新增/编辑表单默认值
const Roles = ref({});                         // 角色下拉选项（后端返回）
const resetPwdFormRef = ref(null);             // 重置密码表单引用（用于校验）

// 表格重渲染key：权限变化时更新，确保列宽度重新计算
const tableRenderKey = ref(1);

// 动态列配置数组：统一管理列的显示、权限、样式（核心配置）
const columns = ref([
  // 无权限控制的基础列
  { prop: 'avatar', label: '头像', width: '80' },
  { prop: 'username', label: '用户名', width: '100' },
  { prop: 'realname', label: '姓名', width: '100' },
  { prop: 'email', label: '邮箱', width: '200' },
  { prop: 'roles', label: '角色', width: '200' },
  { prop: 'status', label: '状态', width: '100' },
  { prop: 'create_time', label: '创建时间', width: '200' },
  { prop: 'last_login', label: '最后登录时间', width: '200' },
  { prop: 'remark', label: '备注' },
  // 有权限控制的列（perm字段为权限标识）
  { prop: 'admin-reset-password', label: '重置密码', width: '120', perm: 'user:admin-reset-password' },
  { prop: 'action', label: '操作', width: '180', align: 'center', fixed: 'right' }
]);

/* -------------------------------------------------
 * 2. 权限判断方法：抽离复杂逻辑，提升模板可读性
 * ------------------------------------------------- */
// 按钮/操作级权限判断
const hasPerm = (perm) => {
  const perms = getPerms();
  return perms.includes(perm);
};

// 列级权限判断：无perm则显示，有perm则校验
const hasColumnPerm = (perm) => {
  return !perm || hasPerm(perm);
};

/* -------------------------------------------------
 * 3. 监听权限变化：触发表格重渲染，避免列宽残留
 * ------------------------------------------------- */
watch(
  () => getPerms(), // 监听权限数组变化
  () => {
    tableRenderKey.value++; // 权限变更时更新key，触发表格重新渲染
  },
  { deep: true } // 深度监听数组内部元素变化
);

/* -------------------------------------------------
 * 4. 事件处理函数：页面交互逻辑（新增、编辑、删除、重置密码等）
 * ------------------------------------------------- */
// 新增用户：打开弹窗并初始化表单
const handleAdd = () => { showDialog(null, 'add'); };
// 编辑用户：填充当前行数据到表单并打开弹窗
const handleEdit = (row) => { showDialog(row, 'edit'); };
// 删除用户：调用删除接口并刷新列表
const handleDelete = (row) => { onDelete(row); };
// 重置密码：保存当前用户并打开弹窗
const handleReset = (row) => { resetPassword(row); };

// 弹窗初始化：区分新增/编辑逻辑
const showDialog = (row, mode) => {
  if (mode === 'edit') {
    Object.assign(form.value, row); // 浅拷贝行数据到表单
    form.value.roles = row.roles.map((role) => role.id); // 角色转id数组
    dialogMode.value = 'edit';
  } else {
    // 新增：清空表单（保留默认状态）
    Object.keys(form.value).forEach((key) => {
      if (key !== 'status') form.value[key] = '';
    });
    dialogMode.value = 'add';
  }
  dialogVisible.value = true;
};

// 重置密码弹窗初始化：保存当前用户并清空表单
const resetPassword = (row) => {
  cur_user.value = row;
  resetPwdForm.pwd1 = '';
  resetPwdForm.pwd2 = '';
  resetPwdDialogVisible.value = true;
};

/* -------------------------------------------------
 * 5. 接口请求函数：与后端交互（查询、新增、编辑、删除、重置密码）
 * ------------------------------------------------- */
// 查询角色列表：用于下拉选择
const requestRole = async () => {
  try {
    const data = await authHttp.getRoleInfo();
    Roles.value = data.results;
  } catch (message) {
    ElMessage.error(message);
  }
};

// 查询用户列表：支持模糊搜索
const requestUser = async (username) => {
  try {
    username = queryForm.value.username;
    const data = await authHttp.getUserInfo(username);
    tableData.value = data.results;
  } catch (message) {
    ElMessage.error(message);
  }
};

// 新增/编辑用户：表单校验后调用对应接口
const requestManagerUser = async () => {
  formRef.value.validate(async (valid) => {
    if (!valid) {
      ElMessage.error('请按要求填写有效的信息');
      return;
    }
    const data = {
      username: form.value.username,
      realname: form.value.realname,
      email: form.value.email,
      password: '123456', // 新增时默认密码
      telephone: form.value.telephone,
      status: form.value.status,
      roles: form.value.roles
    };
    try {
      if (dialogMode.value === 'add') {
        await authHttp.addUser(data);
        ElMessage.success('添加成功');
      } else {
        await authHttp.updateUser(form.value.id, data);
        ElMessage.success('修改成功');
      }
      requestUser(); // 刷新用户列表
      dialogVisible.value = false;
    } catch (message) {
      ElMessage.error(message);
    }
  });
};

// 删除用户：调用删除接口并刷新列表
const onDelete = async (row) => {
  try {
    await authHttp.DeleteUser(row.id);
    ElMessage.success('删除成功');
    requestUser();
  } catch (message) {
    console.error('【catch到的错误】', message);
    ElMessage.error(message);  
  }
};

// 重置密码：调用管理员重置密码接口
const submitResetPassword = async () => {
  if (!resetPwdForm.pwd1 || resetPwdForm.pwd1.length < 6) {
    ElMessage.error('新密码至少 6 位');
    return;
  }
  try {
    await authHttp.changePassword(cur_user.value.id, resetPwdForm.pwd1);
    ElMessage.success('密码重置成功');
    resetPwdDialogVisible.value = false;
  } catch (err) {
    ElMessage.error(err.message || err);
  }
};

/* -------------------------------------------------
 * 6. 生命周期 + 表单校验规则
 * ------------------------------------------------- */
// 页面挂载时：初始化加载用户列表和角色列表
onMounted(() => {
  alert('组件已挂载');   // 最直观
  console.log('当前权限：', getPerms());
  // console.log('是否包含重置密码权限：', getPerms().includes('user:admin-reset-password'));
  requestUser();
  requestRole();
});

// 表单校验规则：element-plus格式，字段级验证
const rules = ref({
  username: [{ required: true, message: '请输入用户名' }],
  email: [
    { required: true, message: '邮箱地址不能为空', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  telephone: [
    { required: true, message: '手机号码不能为空', trigger: 'blur' },
    { pattern: /^1[3|4|5|6|7|8|9][0-9]\d{8}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ],
  realname: [{ required: true, message: '请输入姓名' }]
});
</script>

<style scoped>
/* 表格容器样式：增加顶部间距 */
.table-container {
  margin-top: 16px;
}
</style>