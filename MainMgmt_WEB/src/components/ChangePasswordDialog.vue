<template>
  <el-dialog
    v-model="visible"
    :title="title"
    width="400px"
    @close="reset"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
      <!-- 原密码：仅在修改模式显示 -->
      <el-form-item v-if="mode==='change'" label="原密码" prop="oldPwd">
        <el-input v-model="form.oldPwd" type="password" show-password />
      </el-form-item>

      <el-form-item label="新密码" prop="newPwd">
        <el-input v-model="form.newPwd" type="password" show-password />
      </el-form-item>
      <el-form-item label="确认密码" prop="confirmPwd">
        <el-input v-model="form.confirmPwd" type="password" show-password />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="visible=false">取消</el-button>
      <el-button type="primary" :loading="loading" @click="submit">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, nextTick, computed } from 'vue'
import { ElMessage } from 'element-plus'
import authHttp from '@/api/authHttp'

/* ----------- 基础状态 ----------- */
const visible = ref(false)
const loading = ref(false)
const formRef = ref()

/* ----------- 新增：接收外部参数 ----------- */
const props = defineProps({
  mode: { type: String, default: 'change' },   // change | reset
  api:  { type: Function, default: null }      // 外部传入的管理员重置接口
})

const form = reactive({
  oldPwd: '',
  newPwd: '',
  confirmPwd: ''
})

/* ----------- 动态标题 ----------- */
const title = computed(() => (props.mode === 'change' ? '修改密码' : '重置密码'))

/* ----------- 校验规则 ----------- */
const rules = computed(() => ({
  ...(props.mode === 'change' && { oldPwd: [{ required: true, message: '请输入原密码' }] }),
  newPwd: [
    { required: true, message: '请输入新密码' },
    { min: 6, message: '至少 6 位' }
  ],
  confirmPwd: [
    { required: true, message: '请再次输入新密码' },
    { validator: (_, val, cb) => val === form.newPwd ? cb() : cb(new Error('两次密码不一致')) }
  ]
}))

/* ----------- 开放给父组件 ----------- */
function open(m = 'change') {
  // 如果父组件已经通过 props 传入了 mode，优先使用 props
  visible.value = true
  nextTick(() => formRef.value?.resetFields())
}

/* ----------- 提交 ----------- */
async function submit() {
  await formRef.value.validate(async valid => {
    if (!valid) return
    loading.value = true
    try {
      if (props.mode === 'change') {
        // 个人修改密码接口
        await authHttp.changePassword({
          old_password: form.oldPwd,
          new_password: form.newPwd
        })
      } else {
        // 管理员重置：优先使用外部传入的 api，否则用默认
        const fn = props.api || authHttp.changePassword
        await fn(form.newPwd)   // 仅传新密码
      }
      ElMessage.success(title.value + '成功')
      visible.value = false
      emit('success')
    } catch (e) {
      // console.error('[ChangePasswordDialog] catch →', e)
      ElMessage.error(e)          // ✅ 直接弹字符串
    }finally {
      loading.value = false
    }
  })
}

function reset() {
  formRef.value?.resetFields()
}

defineExpose({ open })
const emit = defineEmits(['success'])
</script>