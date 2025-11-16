<template>
  <svg :style="{ width, height, color: computedColor }" :filter="computedFilter">
    <use :href="prefix + name" fill="currentColor"></use>
  </svg>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  prefix: {
    type: String,
    default: "#icon-"
  },
  // svg名称
  name: String,
  // svg颜色
  color: {
    type: String,
    default: "" // 如果不设置，默认使用 currentColor
  },
  // svg宽度
  width: {
    type: String,
    default: "16px"
  },
  // svg高度
  height: {
    type: String,
    default: "16px"
  },
  // svg滤镜
  filter: {
    type: String,
    default: "" // 可选，默认无滤镜
  }
});

// 计算最终使用的颜色，若未传递 color，则使用 currentColor
const computedColor = computed(() => {
  return props.color || 'currentColor';
});

// 计算滤镜属性
const computedFilter = computed(() => {
  return props.filter ? props.filter : 'none'; // 如果未传入滤镜，则不应用滤镜
});
</script>
