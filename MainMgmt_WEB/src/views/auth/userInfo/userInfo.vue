<!-- ==================== 0. 模板开始 ==================== -->
<template>
  <div>
    <!-- 顶部筛选栏：用户搜索 + 新增按钮 -->
    <el-card>
      <!-- v-model 双向绑定查询关键字；clearable 一键清空 -->
      <el-input
        placeholder="请输入用户名..."
        v-model="queryForm.username"
        clearable
        style="width: 15%"
      />
      <!-- 点击后重新拉取表格数据 -->
      <el-button
        color="#626aef"
        icon="Search"
        @click="requestUser"
        style="margin-left: 0.5%"
      >搜索</el-button>

      <!-- 权限按钮：具备 user:add 权限才渲染 -->
      <el-button
        v-permission="'user:add'"
        color="#626aef"
        icon="Plus"
        @click="handleAdd"
      >新增</el-button>
    </el-card>

    <!-- 表格容器：动态列渲染 + 主题适配 -->
    <!-- 通过 themeStore.theme 动态挂主题类名，实现暗黑/亮色 -->
    <div :class="['table-container', themeStore.theme]">
      <!-- :key="tableRenderKey" 强制重渲染，解决权限切换后列不更新问题 -->
      <el-table :data="tableData" style="width: 100%" :key="tableRenderKey">
        <!-- 遍历 columns 配置，实现“配置驱动”渲染 -->
        <template v-for="(col, index) in columns" :key="`col_${index}_${col.label}_${col.width || ''}`">
          <!-- 先判断当前用户是否拥有该列权限 -->
          <el-table-column
            v-if="hasColumnPerm(col.perm)"
            :label="col.label"
            :width="col.width"
            :align="col.align || 'center'"
            :fixed="col.fixed"
          >
            <!-- 插槽内部根据 col.prop 区分不同列的展示逻辑 -->
            <template #default="scope">
              <!-- 1. 头像列：拼后台静态资源地址 -->
              <template v-if="col.prop === 'avatar'">
                <img :src="imageUrl + scope.row.avatar" alt="头像" width="35" height="35" />
              </template>

              <!-- 2. 角色列：多条目标签 -->
              <template v-else-if="col.prop === 'roles'">
                <el-tag
                  v-for="role in scope.row.roles"
                  :key="role.id"
                  :class="['primary-tag', themeStore.theme]"
                  effect="plain"
                >{{ role.name }}</el-tag>
              </template>

              <!-- 3. 状态列：数字转中文标签 -->
              <template v-else-if="col.prop === 'status'">
                <el-tag v-if="scope.row.status === 1" type="success">正常</el-tag>
                <el-tag v-else-if="scope.row.status === 2" type="warning">未激活</el-tag>
                <el-tag v-else-if="scope.row.status === 3" type="danger">锁定</el-tag>
              </template>

              <!-- 4. 最后登录时间：统一格式化 -->
              <template v-else-if="col.prop === 'last_login'">
                {{ timeFormatter.stringFromDateTime(scope.row.last_login) }}
              </template>

              <!-- 5. 重置密码列：独立按钮 -->
              <template v-else-if="col.prop === 'resetpwd'">
                <el-button
                  v-permission="'user:resetpwd'"
                  type="primary"
                  @click="handleReset(scope.row)"
                   >重置密码</el-button>
              </template>   
              <!-- 6. 操作列：编辑/删除，再次权限判断 -->
              <template v-else-if="col.prop === 'action'">
                <div style="display: flex; justify-content: space-around;">
                  <operation-button
                    v-permission="'user:edit'"
                    type="edit"
                    @click="handleEdit(scope.row)"
                  />
                  <operation-button
                    v-permission="'user:delete'"
                    type="delete"
                    @click="handleDelete(scope.row)"
                  />
                </div>
              </template>

              <!-- 7. 默认列：直接输出字段值 -->
              <template v-else>{{ scope.row[col.prop] }}</template>
            </template>
          </el-table-column>
        </template>
      </el-table>
    </div>

    <!-- 新增 / 编辑 用户对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'edit' ? '修改用户' : '新增用户'"
      width="25%"
      style="padding-right: 3%"
    >
      <!-- 表单校验：rules 绑定下方 reactive 对象 -->
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" />
          <!-- 友好提示：初始密码固定 123456 -->
          <el-alert title="默认初始密码：123456" :closable="false" type="success" style="line-height: 10px" />
        </el-form-item>

        <el-form-item label="姓名" prop="realname"><el-input v-model="form.realname" /></el-form-item>
        <el-form-item label="手机号" prop="telephone"><el-input v-model="form.telephone" /></el-form-item>
        <el-form-item label="邮箱" prop="email"><el-input v-model="form.email" /></el-form-item>

        <!-- 状态：单选组，值 1 正常 / 3 禁用 -->
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio :value="1">正常</el-radio>
            <el-radio :value="3">禁用</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 角色：多选下拉，绑定的是角色 id 数组 -->
        <el-form-item label="角色">
          <el-select style="width: 100%" v-model="form.roles" multiple>
            <el-option v-for="i in Roles" :key="i.id" :label="i.name" :value="i.id" />
          </el-select>
        </el-form-item>
      </el-form>

      <!-- 底部按钮组 -->
      <template #footer>
        <el-button color="#626aef" plain @click="dialogVisible = false">取消</el-button>
        <!-- 点击后先走表单校验，再走新增/修改接口 -->
        <el-button color="#626aef" plain @click="requestManagerUser">确认</el-button>
      </template>
    </el-dialog>

    <!-- 复用 ChangePasswordDialog 组件：mode="reset" 表示管理员重置 -->
    <ChangePasswordDialog
      ref="pwdDialogRef"
      mode="reset"
      :api="doAdminResetPwd"
      @success="onResetSuccess"
    />
  </div>
</template>

<!-- ==================== 1. 逻辑脚本开始 ==================== -->
<script setup>
/* -------------------------------------------------
 * 0. 引入依赖
 * ------------------------------------------------- */
import authHttp from '@/api/authHttp';          // 封装好的用户/角色相关接口
import { ref, reactive, onMounted, watch } from 'vue';
import { ElMessage } from 'element-plus';      // 消息提示
import timeFormatter from '@/utils/timeFormatter';
import OperationButton from '@/components/OperationButton.vue'; // 封装编辑/删除小按钮
import { useThemeStore } from '@/stores/theme'; // pinia 主题仓库
import { getPerms } from '@/utils/permission';   // 取当前用户权限数组
// import { getParsedPermissions } from '@/utils/permission';
import ChangePasswordDialog from '@/components/ChangePasswordDialog.vue'; // 重置密码弹窗

/* -------------------------------------------------
 * 2. 响应式数据
 * ------------------------------------------------- */
const themeStore     = useThemeStore();   // 主题
const tableRenderKey = ref(1);            // 表格 key，强制重渲染
const cur_user       = ref();             // 当前要重置密码的用户
const imageUrl       = import.meta.env.VITE_BASE_URL + '/media/userAvatar/'; // 头像静态资源前缀
const dialogVisible  = ref(false);        // 新增/编辑 弹窗显隐
const dialogMode     = ref('add');        // 弹窗模式 add | edit
const tableData      = ref([]);           // 表格数据
const queryForm      = ref({});           // 顶部搜索条件
const formRef        = ref(null);         // el-form 引用，用于校验
const form           = ref({ status: 1 }); // 表单双向绑定对象，默认状态正常
const Roles          = ref({});           // 所有角色下拉数据源
// 1. 声明要抛出的事件
const emit = defineEmits(['success', 'fail'])

/* -------------------------------------------------
 * 3. 表格列配置：label/width/对齐/权限 一目了然
 * ------------------------------------------------- */
const columns = ref([
  { prop: 'avatar',     label: '头像',       width: '80' },
  { prop: 'username',   label: '用户名',     width: '100' },
  { prop: 'realname',   label: '姓名',       width: '100' },
  { prop: 'email',      label: '邮箱',       width: '200' },
  { prop: 'roles',      label: '角色',       width: '200' },
  { prop: 'status',     label: '状态',       width: '100' },
  { prop: 'create_time',label: '创建时间',   width: '200' },
  { prop: 'last_login', label: '最后登录时间', width: '200' },
  { prop: 'remark',     label: '备注' },
  // 这两列需要额外权限才能看见
  { prop: 'resetpwd',   label: '重置密码',   width: '120', perm: 'user:resetpwd' },
  { prop: 'action',     label: '操作',       width: '180', align: 'center', fixed: 'right' }
]);

/* -------------------------------------------------
 * 4. 权限判断函数
 * ------------------------------------------------- */
// 单一权限
const hasPerm = perm => getPerms().includes(perm);
// 列权限：如果没配置 perm 则默认放行
const hasColumnPerm = perm => !perm || hasPerm(perm);

// 当权限数组变化时，给表格换一个 key，达到“重新挂载”效果
watch(getPerms, () => tableRenderKey.value++, { deep: true });

/* -------------------------------------------------
 * 5. 事件处理：增删改查 打开弹窗 重置密码
 * ------------------------------------------------- */
const handleAdd  = () => showDialog(null, 'add');
const handleEdit = row => showDialog(row, 'edit');
const handleDelete = row => onDelete(row);
const pwdDialogRef = ref(null);

// 打开弹窗并做初始化
const showDialog = (row, mode) => {
  dialogMode.value = mode;
  if (mode === 'edit') {
    // 编辑：深拷贝行数据 + 把角色对象数组转成 id 数组
    Object.assign(form.value, row);
    form.value.roles = row.roles.map(r => r.id);
  } else {
    // 新增：清空旧数据，只保留默认状态
    Object.keys(form.value).forEach(k => { if (k !== 'status') form.value[k] = '' });
  }
  dialogVisible.value = true;
};

// 重置密码：把当前行缓存起来，然后打开复用组件

const handleReset = row => {
  cur_user.value = row;
  pwdDialogRef.value.open();
};

/* -------------------------------------------------
 * 6. 接口请求
 * ------------------------------------------------- */
// 拉角色下拉
const requestRole = async () => {
  try { Roles.value = (await authHttp.getRoleInfo()).results }
  catch (e) { ElMessage.error(e) }
};

// 拉用户表格
const requestUser = async () => {
  try { tableData.value = (await authHttp.getUserInfo(queryForm.value.username)).results }
  catch (e) { ElMessage.error(e) }
};

// 新增 or 编辑 确定按钮
const requestManagerUser = async () => {
  // 先走 el-form 校验
  await formRef.value.validate(async valid => {
    if (!valid) return ElMessage.error('请按要求填写有效信息');
    // 组装 payload
    const data = {
      username: form.value.username,
      realname: form.value.realname,
      email: form.value.email,
      password: '123456',          // 后台要求必传初始密码
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
      // 重新拉表格 & 关闭弹窗
      requestUser();
      dialogVisible.value = false;
      //  ElMessage.error(e.message) 弹出红框
    } catch (e) { ElMessage.error(e) }
  });
};

// 删除
const onDelete = async row => {
  try {
    await authHttp.DeleteUser(row.id);
    ElMessage.success('删除成功');
    requestUser();
  } catch (e) { ElMessage.error(e) }
};

// 提供给 ChangePasswordDialog 的重置接口
const doAdminResetPwd = async (newPwd) => {
  await authHttp.changePassword({
    user_id: cur_user.value.id,
    new_password: newPwd
  });
};

// 重置成功回调
const onSuccess = () => {
  // ElMessage.success(title.value + '成功')   // ← 删掉这一行
  emit('success')   // 只抛事件给父组件
}

/* -------------------------------------------------
 * 7. 生命周期 & 表单校验规则
 * ------------------------------------------------- */
onMounted(() => {
  requestUser();  // 先拉表格
  requestRole();  // 再拉角色下拉
});

// 表单校验规则（el-form 的 :rules 绑定它）
const rules = ref({
  username: [
    { required: true, message: '请输入用户名' }
  ],
  email: [
    { required: true, message: '邮箱地址不能为空', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  telephone: [
    { required: true, message: '手机号码不能为空', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ],
  realname: [
    { required: true, message: '请输入姓名' }
  ]
});
</script>

<!-- ==================== 2. 样式 ==================== -->
<style scoped>
    /* 仅仅给表格上方留一点间距 */
    .table-container {
      margin-top: 16px;
    }
</style>