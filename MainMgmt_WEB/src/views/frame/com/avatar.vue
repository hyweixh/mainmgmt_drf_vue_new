<template>
  <el-dropdown>
    <span class="el-dropdown-link">
      <el-avatar shape="square" :size="35" :src="avatarUrl" />
      <span v-if="authStore.user" style="margin-left: 10px">
        {{ authStore.user.realname }}
      </span>
    </span>

    <template #dropdown>
      <el-dropdown-menu>
        <!-- 1. 修改密码-->
        <el-dropdown-item @click="onChpwdDialog">
          修改密碼
        </el-dropdown-item>
        <el-dropdown-item divided @click="onExit">退出登录</el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>

  <!-- 2. 挂载共用弹窗 -->
  <ChangePasswordDialog ref="pwdDialog" @success="onExit" />
</template>

<script setup>
import router from '@/router'
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import ChangePasswordDialog from '@/components/ChangePasswordDialog.vue'

const authStore = useAuthStore()

// 头像地址
const avatarUrl = `${import.meta.env.VITE_BASE_URL}/media/userAvatar/${authStore.user.avatar}`

// 修改密码：先提示，再弹出对话框
const pwdDialog = ref()
const onChpwdDialog = () => {
  // ElMessage.success('你真的要修改密码吗？')
  pwdDialog.value.open('change')   // change = 修改密码模式
}

// 退出登录
const onExit = () => {
  localStorage.removeItem('tabs')
  localStorage.removeItem('activeTab')
  authStore.clearUserToken()
  router.push({ name: 'login' })
}
</script>

<style scoped>
.el-dropdown-link {
  display: flex;
  align-items: center;
  outline: none;
}
</style>