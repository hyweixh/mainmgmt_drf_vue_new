<template>
  <div class="login-container">
    <div class="test"></div>
    <div class="wow-bg-cc">
      <h3 class="colorboard">维护管理</h3>
      <p class="text-muted">登录您的帐户</p>
      <el-form :model="form" status-icon @submit.prevent>
        <el-form-item :rules="[{ required: true, message: '请输入用户名', trigger: 'blur' }]" class="loginInput">
          <el-input v-model="form.username" prefix-icon="User" size="large" placeholder="Username" />
        </el-form-item>
        <el-form-item :rules="[{ required: true, message: '请输入密码', trigger: 'blur' }]" class="loginInput">
          <el-input v-model="form.password" prefix-icon="Lock" size="large" type="password" placeholder="Password"
            show-password />
        </el-form-item>
        <el-form-item>
          <el-button color="#1C1F2F" round size="large" class="loginButton" :loading="loginLoading" 
            @click="onSubmit" @keydown.enter="keyDown()">
            {{ loginLoading ? '登录中...' : '登录' }}
          </el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted, onUnmounted } from 'vue'
import { ElMessage} from 'element-plus'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import authHttp from '@/api/authHttp'

const router = useRouter()
const authStore = useAuthStore()

// 登录表单数据
const form = reactive({ username: '', password: '' })
// 登录按钮加载状态
const loginLoading = ref(false)

// 登录按钮点击事件
const onSubmit = async () => {
  if (!form.username) return ElMessage.error('请输入用户名')
  if (!form.password) return ElMessage.error('请输入密码')

  loginLoading.value = true
  try {
    const data = await authHttp.login(form.username, form.password)
    const { token, user, menus, permissions } = data
    
    authStore.setUserToken(user, token, menus, permissions)
    ElMessage.success('登录成功')
    router.push({ name: 'home' })
  } catch (e) {
    // ✅ 简洁稳定的错误处理
    const errorMsg = e?.response?.data?.message || e?.message || '登录失败，请重试'
    ElMessage.error(errorMsg)
  } finally {
    loginLoading.value = false
  }
}

// 回车键登录
const keyDown = (e) => {
  if (e.key === 'Enter') {
    onSubmit()
  }
}

// 挂载时绑定键盘事件
onMounted(() => {
  window.addEventListener('keydown', keyDown)
})

// 卸载时解绑键盘事件
onUnmounted(() => {
  window.removeEventListener('keydown', keyDown, false)
})
</script>

<style>
body {
  background-color: #181828;
  margin: 0;
  padding: 0;
}
</style>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  position: relative;
  top: 15vh;
}

.wow-bg-cc {
  background-color: #141421;
  border: 1px solid #2e2e4c;
  box-shadow:
    3px 9px 16px rgb(0, 0, 0, 0.4),
    -3px -3px 10px rgba(255, 255, 255, 0.06),
    inset 14px 14px 26px rgb(0, 0, 0, 0.3),
    inset -3px -3px 15px rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  margin-top: 4px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  width: 350px;
}

.test {
  background-color: #00ffaaed;
  border: none;
  border-radius: 30px;
  height: 120px;
  width: 350px;
  position: absolute;
  top: -1px;
  left: 50%;
  transform: translateX(-50%);
  z-index: -1;
}

/* 输入框样式 */
:deep(.el-input__wrapper) {
  background-color: #161624;
  box-shadow:
    0 -2px 2px rgba(137, 137, 137, 0.2),
    0 0 0 0.5px #2e344d inset;
  font-size: 18px;
  font-family: 'Microsoft YaHei', 'Verdana';
  transition: all 0.3s ease;
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow:
    0 -2px 2px rgba(137, 137, 137, 0.2),
    0 0 0 0.5px #00ffaaed inset;
}

:deep(.el-input__inner) {
  font-weight: bold;
  font-family: 'Microsoft YaHei', 'Verdana', sans-serif;
}

:deep(.el-input__inner::placeholder) {
  color: var(--el-input-text-color);
}

.loginInput {
  width: 85%;
  margin: 0 auto;
  margin-top: 30px;
}

.colorboard {
  color: #00ffaaed;
  font-weight: bold;
  margin-top: 15px;
  margin-bottom: 0px;
  font-size: 28px;
}

.text-muted {
  color: #6c757d;
  margin-top: 10px;
  margin-bottom: 0px;
  font-size: 16px;
}

.login-form {
  width: 100%;
  margin-top: -10px;
}

.loginButton {
  width: 300px;
  margin: 0 auto;
  margin-top: 30px;
}

:deep(.el-button > span) {
  font-size: 18px;
}

.el-button:hover {
  background-color: #1c1f2f;
  border-color: #2e344d;
  box-shadow: 0 4px 16px rgba(74, 74, 74, 0.5);
  border-style: solid;
  border-width: 1px 0px 0px 1px;
  border-radius: 50px;
}

:deep(.el-input.is-disabled .el-input__wrapper) {
  background-color: #161624;
  box-shadow:
    0 -2px 2px rgba(137, 137, 137, 0.2),
    0 0 0 0.5px #2e344d inset;
}
</style>