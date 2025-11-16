
<script setup>
import { useThemeStore } from '@/stores/theme';
const themeStore = useThemeStore();


</script>
<template>
  <!-- begin loading-cubes modal -->
  <div :class="['loading-div',themeStore.theme]">
    <div class="loading-cubes">
    <div class="loading-sk-cube loading-sk-cube1"></div>
    <div class="loading-sk-cube sk-cube2"></div>
    <div class="loading-sk-cube sk-cube3"></div>
    <div class="loading-sk-cube sk-cube4"></div>
    <div class="loading-sk-cube sk-cube5"></div>
    <div class="loading-sk-cube sk-cube6"></div>
    <div class="loading-sk-cube sk-cube7"></div>
    <div class="loading-sk-cube sk-cube8"></div>
    <div class="loading-sk-cube sk-cube9"></div>
  </div>
  <div><el-text class="loading-text">玩命加载中...</el-text></div>
  </div>


</template>

<script setup>
</script>

<style>
/*  begin loading-cubes css */

.loading-div {
  position: absolute; /* 使动画固定在屏幕上 */
  z-index: 9999; /* 保证它位于页面的最上层 */
  display: flex;
  flex-direction: column; /* 垂直排列动画和文字 */
  align-items: center; /* 横向居中 */
  justify-content: center; /* 纵向居中 */
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
}

.loading-text{
  font-size: 14px;
}

.loading-div.dark{
  background-color: rgba(0, 0, 0, 0.5); /* 半透明的黑色背景 */
}

.loading-div.light{
  background-color: rgba(255, 255, 255, 0.35);
}


.loading-cubes {
  width: 40px;
  height: 40px;
  display: grid; /* 使用 grid 布局 */
  grid-template-columns: repeat(3, 1fr); /* 三列 */
  grid: 2px; /* 设置格子之间的间距 */
}

.loading-cubes .loading-sk-cube {
  width: 100%;
  height: 100%;
  background-color: var(--el-color-primary);
  float: left;
  animation: sk-cubeGridScaleDelay 1.3s infinite ease-in-out;
}

.loading-cubes .loading-sk-cube1 {
  animation-delay: 0.2s;
}

.loading-cubes .sk-cube2 {
  animation-delay: 0.3s;
}

.loading-cubes .sk-cube3 {
  animation-delay: 0.4s;
}

.loading-cubes .sk-cube4 {
  animation-delay: 0.1s;
}

.loading-cubes .sk-cube5 {
  animation-delay: 0.2s;
}

.loading-cubes .sk-cube6 {
  animation-delay: 0.3s;
}

.loading-cubes .sk-cube7 {
  animation-delay: 0s;
}

.loading-cubes .sk-cube8 {
  animation-delay: 0.1s;
}

.loading-cubes .sk-cube9 {
  animation-delay: 0.2s;
}

@keyframes sk-cubeGridScaleDelay {

  0%,
  70%,
  100% {
    transform: scale3D(1, 1, 1);
  }

  35% {
    transform: scale3D(0, 0, 1);
  }
}
</style>