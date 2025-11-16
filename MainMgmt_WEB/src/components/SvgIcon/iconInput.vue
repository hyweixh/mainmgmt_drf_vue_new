<template>
  <div class="svg-selector-container">
    <el-input v-model="localValue" placeholder="选择图标" @click="toggleDropdown" readonly>
      <template #suffix>
        <el-icon>
          <component :is="suffixIcon" @click="toggleDropdownIcon" />
        </el-icon>
      </template>
    </el-input>
    <transition name="dropdown">
      <div v-if="showDropdown" :class="['svg-dropdown', themeStore.theme]">
        <div v-for="(svg, index) in svgFiles" :key="index" :class="['svg-item', themeStore.theme]" @click="selectIcon(svg)">
          <img :src="svg.path" :alt="svg.name" class="svg-image" />
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount, computed } from 'vue'
import { useThemeStore } from '@/stores/theme'
const themeStore = useThemeStore()

const props = defineProps({
  modelValue: String,
})

const emit = defineEmits(['update:modelValue'])

const localValue = ref(props.modelValue || '')
const svgFiles = ref([])

// const svgModules = import.meta.glob('/src/assets/icons/*.svg')
// for (const path in svgModules) {
//   svgModules[path]().then((module) => {
//     svgFiles.value.push({
//       path: module.default,
//       name: getFileName(path)
//     })
//   })
// }
// const svgModules = import.meta.glob('/scr/assets/icons/*.svg')
// '/scr/assets/icons/*.svg'方式有时会引用绝对目录导致出错
const svgModules = import.meta.glob('../../assets/icons/*.svg')
for (const path in svgModules) {
  svgModules[path]()
    .then((module) => {
      console.log('加载成功:', path, 'module.default:', module.default) // ← 关键日志
      svgFiles.value.push({
        path: module.default,
        name: getFileName(path)
      })
    })
    .catch((err) => {
      console.warn('加载失败:', path, err)
    })
}

const showDropdown = ref(false)
const suffixIcon = computed(() => (showDropdown.value ? 'ArrowUp' : 'ArrowDown'))

const toggleDropdown = () => {
  showDropdown.value = !showDropdown.value
}

const toggleDropdownIcon = (event) => {
  event.stopPropagation()
  toggleDropdown()
}

const getFileName = (path) => {
  const cleanPath = path.split('?')[0]
  return cleanPath.split('/').pop().replace('.svg', '')
}

const selectIcon = (svg) => {
  localValue.value = svg.name
  emit('update:modelValue', svg.name)
  showDropdown.value = false
}

const handleClickOutside = (event) => {
  const dropdown = document.querySelector('.svg-selector-container')
  if (dropdown && !dropdown.contains(event.target)) {
    showDropdown.value = false
  }
}

onMounted(() => {
  window.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  window.removeEventListener('click', handleClickOutside)
})

watch(() => props.modelValue, (newValue) => {
  localValue.value = newValue
})
</script>

<style scoped>
.svg-selector-container {
  position: relative;
  width: 100%;
}

.dropdown-enter-active,
.dropdown-leave-active {
  transition: height 0.3s ease-in-out, opacity 0.3s ease-in-out;
}

.dropdown-enter-from {
  height: 0;
  opacity: 0;
}

.dropdown-enter-to {
  height: auto;
  opacity: 1;
}

.dropdown-leave-from {
  height: auto;
  opacity: 1;
}

.dropdown-leave-to {
  height: 0;
  opacity: 0;
}

.svg-dropdown {
  position: absolute;
  max-height: 210px;
  overflow-y: auto;
  z-index: 10;
  display: flex;
  flex-wrap: wrap;
  gap: 4%;
  padding-left: 5%;
  padding-right: 5%;
}

.svg-dropdown.light {
  border: 1px solid #ddd;
  background-color: #fff;
}

.svg-dropdown.dark {
  border: 1px solid #323232;
  background-color: var(--dark-background-card);
}

.svg-item {
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  width: calc(20% - 10px);
  margin-bottom: 5%;
}

.svg-item.light:hover {
  background-color: #f0f0f0;
}

.svg-item.dark:hover {
  background-color: #3d3c3c;
}

.svg-image {
  width: 30px;
  height: 30px;
}

:deep(.el-input__inner) {
  cursor: pointer;
}

:deep(.el-input__suffix) {
  cursor: pointer;
}
</style>
