<template>
  <el-progress :percentage="animatedPercentage" :stroke-width="strokeWidth" :show-text="showText" :color="color" />
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';

// 定义组件的 props
const props = defineProps({
  // 进度条的百分比，必填
  percentage: {
    type: Number,
    required: true
  },
  // 进度条的宽度，默认为 10
  strokeWidth: {
    type: Number,
    default: 10
  },
  // 控制是否显示百分比文本
  showText: {
    type: Boolean,
    default: true
  },
  // 颜色
  color: {
    type: String,
    default: '#626aef'
  }
});

// 用于动画效果的响应式数据，初始为 0
const animatedPercentage = ref(0);

// 动画函数
const animate = () => {
  animatedPercentage.value = 0;     // 初始值

  setTimeout(() => {
    // 设置 animatedPercentage 为 props 中的 percentage
    animatedPercentage.value = props.percentage;
  }, 200); 
};

// 监听 props.percentage 的变化，触发动画函数
watch(() => props.percentage, animate);

// 组件挂载时立即执行动画函数
onMounted(animate);
</script>
