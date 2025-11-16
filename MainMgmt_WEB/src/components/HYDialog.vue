<script setup>  
import { ref } from 'vue';  
  
// 假设这个组件需要从外部接收一个v-model绑定的值来控制对话框的显示隐藏  
// 我们通常使用props接收modelValue（或自定义的prop名），并通过emits发送update:modelValue来更新它  
// 但在这个例子中，为了简单起见，我们直接在内部使用ref来控制，并通过自定义事件来通知外部  
const dialogVisible = ref(false); // 使用ref来创建一个响应式的变量来控制对话框的显示隐藏  
  
// 定义接收的属性  
const props = defineProps({  
    title: {  
        type: String,  
        default: '' // 默认的对话框标题为空  
    },  
    width: {  
        type: String,  
        default: '500px' // 默认的对话框宽度，注意通常我们会加上'px'单位  
    }  
});  
  
// 定义可以触发的自定义事件  
const emits = defineEmits(['cancel', 'submit']);  
  
// 取消按钮的点击事件处理函数  
const onCancel = () => {  
    // console.log('Cancel button clicked'); 
    dialogVisible.value = false; // 隐藏对话框  
    emits('cancel') // 触发cancel事件  
};  
  
// 提交按钮的点击事件处理函数  
const onSubmit = () => {  
    emits('submit'); // 触发submit事件  
    // 这里可以根据需要添加其他逻辑，比如表单验证、提交数据等  
};  
  
// 注意：在Vue 3的<script setup>中，不需要显式地声明props或emits的变量，  
// 因为defineProps和defineEmits会自动处理这些。但在这里为了清晰起见，我还是保留了它们。  
</script>  
  
<template>  
  <el-dialog  v-model="dialogVisible" :title="props.title" :width="props.width">    
    <!-- 这里使用slot来允许父组件插入自定义内容 -->  
    <slot></slot>  
    <!-- 自定义的footer插槽 -->  
    <template #footer>  
      <div class="dialog-footer">  
        <el-button @click="onCancel">取消</el-button>  
        <el-button type="primary" @click="onSubmit">确认</el-button>  
        
      </div>  
    </template>  
  </el-dialog>  
</template>  
  
<style scoped>  
</style> 
