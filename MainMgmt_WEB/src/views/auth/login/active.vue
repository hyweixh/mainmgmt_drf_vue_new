<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import authHttp from '@/api/authHttp';

// 获取路由信息
const route = useRoute();
// 路由跳转
const router = useRouter();

// 激活状态
const activationStatus = ref(null);
// 激活消息
const activationMessage = ref('');
// 倒计时初始化为5秒
const countdown = ref(5);

onMounted(async () => {
  const token = route.query.token;  // 从URL查询参数中获取token
  if (token) {
    try {
      let data = await authHttp.activeStaff(token);
      console.log("API response:", data);
      activationStatus.value = 'success';
      activationMessage.value = '账户激活成功！';
      startCountdown(); //倒计时处理
    } catch (error) {
      console.error("API error:", error);
        activationStatus.value = 'error';
        activationMessage.value = error;
    }
  }
});

// 倒计时函数
const startCountdown = () => {
  const interval = setInterval(() => {
    if (countdown.value > 0) {
      countdown.value--;
    } else {
      clearInterval(interval);
      router.push('/login');
    }
  }, 1000);
};
</script>

<template>
  <div v-if="activationStatus === 'success'" class="success-message">
    <el-result icon="success" title="激活成功" sub-title="您的账户已成功激活，现在可以登录了。">
      <template #extra>
        <div>
          <el-link type="success" @click="router.push('/login')">点击立即登录，系统将在 {{countdown}} 秒后自动跳转到登录页。</el-link>
        </div>
      </template>
    </el-result>
  </div>
  <div v-else-if="activationStatus === 'warning'" class="error-message">
    <el-result icon="warning" title="激活失败" :sub-title="activationMessage" />
  </div>
  <div v-else class="error-message">
    <el-result icon="error" title="激活失败" :sub-title="activationMessage" />
  </div>
</template>

<style scoped>
.success-message,
.error-message {
  display: flex;        /* 使用Flexbox布局 */
  align-items: center;    /* 垂直居中 */
  justify-content: center; /* 水平居中 */
  height: 100vh;          /* 高度为视口高度 */
  margin: 0;            /* 去除外边距 */
}
</style>
