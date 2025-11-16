<template>
  <div class="svg-container">
    <div v-for="(svgPath, index) in svgFiles" :key="index" class="svg-item">
      <!-- 显示 SVG 图片 -->
      <img :src="svgPath.path" :alt="svgPath.name" class="svg-image" />
      <!-- 显示 SVG 文件名 -->
      <p>{{ svgPath.name }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// 使用 import.meta.glob 动态导入 assets/icons 目录下的所有 .svg 文件
const svgFiles = ref([])

// Glob 引入 SVG 文件
const svgModules = import.meta.glob('/src/assets/icons/*.svg')

// 将 SVG 文件的路径存储到数组中，使用异步方式处理模块
for (const path in svgModules) {
  svgModules[path]().then((module) => {
    svgFiles.value.push({
      path: module.default,
      name: getFileName(path)
    })
  })
}

// 提取文件名函数
const getFileName = (path) => {
  // 去掉 URL 参数部分（即 "?" 后的内容）
  const cleanPath = path.split('?')[0]
  // 提取文件名并去掉 .svg 后缀
  return cleanPath.split('/').pop().replace('.svg', '')
}
</script>

<style scoped>
.svg-container {
  display: flex;
  flex-wrap: wrap;
}

.svg-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 10px;
}

.svg-image {
  width: 50px;
  height: 50px;
  margin-bottom: 5px;
}
</style>
