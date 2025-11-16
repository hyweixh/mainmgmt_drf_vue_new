<template>
  <div :class="wrapperClass">
      <!-- 显示总条目数 -->
      <el-text style="margin-right: 10px;">共{{ total }}条</el-text>
      <!-- 每页显示条目数选择框 -->
      <el-form-item style="margin: 0;">
          <el-select v-model="localPageSize" style="width: 100px; margin-right: 10px;">
              <el-option label="10条/页" :value="10" />     <!-- 保留给consul添加虚拟机 -->
              <el-option label="15条/页" :value="15" />
              <el-option label="20条/页" :value="20" />
              <el-option label="50条/页" :value="50" />
              <el-option label="100条/页" :value="100" />
          </el-select>
      </el-form-item>
      <!-- 分页组件 -->
      <el-pagination background layout="prev, pager, next" :total="total" v-model:current-page="localPage"
          :page-size="localPageSize" style="margin-right: 10px;" />
      <!-- 跳转到指定页码输入框 -->
      <el-form-item style="margin: 0;">
        <el-text style="margin-right: 4px;">前往:</el-text>
          <el-input type="number" v-model.number="inputPage" style="width: 55px;" @keyup.enter="jumpToPage" />
          <el-text >页</el-text>
      </el-form-item>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'

// 定义组件的 props
const props = defineProps({
  // 总页数
  total: {        
      type: Number,
      required: true
  },
  //当前页
  page: {
      type: Number,
      default: 1
  },
  // 每页条数
  pageSize: {
      type: Number,
      default: 15
  },
  wrapperClass: { type: String, default: 'page' }, // 外层 class
})

// 定义组件的 emits
const emit = defineEmits(['update:page', 'update:pageSize'])

// 本地状态，维护当前页码和每页显示条目数
const localPage = ref(props.page)
const localPageSize = ref(props.pageSize)
const inputPage = ref(1) // 跳转页码的输入框值

// 监听当前页码的变化，并触发 'update:page' 事件
watch(() => localPage.value, (newPage) => {
  emit('update:page', newPage)
})

// 监听每页显示条目数的变化
watch(() => localPageSize.value, (newPageSize) => {
  if (localPage.value === 1) {
      // 如果当前页码是第一页，仅更新每页条目数
      emit('update:pageSize', newPageSize)
  } else {
      // 如果当前页码不是第一页，将页码设置为第一页并更新每页条目数
      localPage.value = 1
      emit('update:page', 1)
      emit('update:pageSize', newPageSize)
  }
})

// 监听 props.page 的变化，并同步更新 localPage
watch(() => props.page, (newPage) => {
  localPage.value = newPage
})

// 跳转到指定页码的方法
const jumpToPage = () => {
  // 检查输入的页码是否有效
  if (inputPage.value > 0 && inputPage.value <= Math.ceil(props.total / localPageSize.value)) {
      localPage.value = inputPage.value
  } else {
      // 如果无效，显示错误消息
      ElMessage.error("输入的页码无效")
  }
}
</script>
<style>
.page{
  display: flex; 
  justify-content: flex-end; 
  align-items: center; 
  margin-top: 10px;
}
</style>