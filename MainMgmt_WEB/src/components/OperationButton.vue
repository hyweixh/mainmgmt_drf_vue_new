<template>
  <div>
    <el-button v-if="type === 'view'" class="icon-view" color="#626aef" plain icon="view" @click="emitClick" :title="'查看'">
      {{ label }}
    </el-button>
    <el-button v-if="type === 'edit'" class="icon-edit" color="#FAC858" plain icon="Edit" @click="emitClick" :title="'编辑'">
      {{ label }}
    </el-button>
    <el-button v-if="type === 'copy'" class="icon-copy" color="#626aef" plain icon="CopyDocument" @click="emitClick" :title="'复制'">
      {{ label }}
    </el-button>
    <el-button v-if="type === 'test'" class="icon-test" color="#4FC08D" plain icon="Position" @click="emitClick" :title="'测试连接'">
      {{ label }}
    </el-button>
    <el-popconfirm v-if="type === 'delete'" :title="deleteTitle" :width=width @confirm="emitClick">
      <template #reference>
        <el-button class="icon-delete" :color="deleteColor" icon="Delete" plain :title="'删除'">
          {{ label }}
        </el-button>
      </template>
    </el-popconfirm>
  </div>
</template>

<script setup>

// 定义 props，用于接收父组件传递的参数(隐式使用)
const { type, label, deleteColor, deleteTitle } = defineProps({
  type: {
    required: true,
    validator: value => ['view','edit', 'copy','delete','test'].includes(value),
  },
  label: {
    default: ''
  },
  editColor: {
    default: '#FAC858',
  },
  deleteColor: {
    default: '#F56C6C',
  },
  deleteTitle: {
    type: String,
    default: '确认删除吗?',
  },
  width: {
    type: String,
    default: 'auto', // 默认宽度为自动
  }
});

// 定义 emits，用于发出事件
// defineEmits 用于定义组件能发出哪些事件
const emit = defineEmits(['click']);

// 定义 emitClick 方法，用于发出 'click' 事件
const emitClick = () => {
  emit('click');
};
</script>

<style>


/* 统一按钮样式 */
.icon-test,
.icon-view,
.icon-copy,
.icon-edit,
.icon-delete,
.icon-black {
  background: transparent;
  border: none ;
  box-shadow: none ;
  padding: 4px 8px ; /* 设置合适的内边距 */
  margin: 0 ;
  font-size: 18px;
  height: 15px ; /* 固定按钮高度 */
  line-height: 1 ;
  min-height: unset ; /* 重置最小高度 */
}

.icon-test:hover {
  background: transparent;
  color: #4fc08d;
}

.icon-edit:hover {
  background: transparent;
  color: #fac858;
}

.icon-view:hover,
.icon-copy:hover {
  background: transparent;
  /* 悬停时背景仍然透明 */
  color: #626aef;
}

.icon-delete:hover {
  background: transparent;
  /* 悬停时背景仍然透明 */
  color: #f56c6c;
}

.icon-edit:focus,
.icon-delete:focus {
  outline: none;
  /* 去除默认的焦点样式 */
  box-shadow: none;
  /* 去除焦点时的阴影 */
}
</style>