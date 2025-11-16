<template>
  <div class="not-found-or-forbidden">
    <!-- 左侧提示信息 -->
    <div class="message">
      <h1>Oops!</h1>
      <p>您没有权限或者页面不存在</p>
      <!-- 按钮在提示信息的下方 -->
      <el-button @click="goHome" class="back-home-button">
        返回主页
      </el-button>
    </div>
    <!-- 右侧动态图片 -->
    <div class="image">
      <img src="@/assets/images/401.gif" alt="No Access or Not Found" />
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';

const router = useRouter();

// 返回首页
const goHome = () => {
  router.push({ name: 'home' });
};
</script>

<style scoped>
.not-found-or-forbidden {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 85vh;
  padding: 20px;
  margin-top: 1%;
}

.message {
  flex: 1;
  max-width: 25%;
  text-align: left; /* 左对齐提示信息 */
}

.message h1 {
  font-size: 48px; /* 3rem 转换为 px (3 * 16px) */
  color: #e74c3c;
  margin-bottom: 10px;
}

.message p {
  font-size: 24px; /* 1.5rem 转换为 px (1.5 * 16px) */
  color: #555;
  margin-bottom: 20px;
}

.back-home-button {
  padding: 10px 20px;
  font-size: 19px; /* 1.2rem 转换为 px (1.2 * 16px) */
  color: white;
  background-color: #3498db;
  border: none;
  cursor: pointer;
  border-radius: 5px;
  transition: background-color 0.3s;
}

.back-home-button:hover {
  background-color: #2980b9;
}

.image {
  flex: 1;
  max-width: 20%;
  text-align: right; /* 图片右对齐 */
}

.image img {
  max-width: 100%;
  height: auto;
}
</style>
