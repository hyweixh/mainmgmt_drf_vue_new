<script setup>
import { useAuthStore } from '@/stores/auth';
import { computed } from 'vue';

const AuthStore = useAuthStore();

const props = defineProps({
  isCollapse: { type: Boolean, default: false },
  defaultActive: { type: String }
});

// ✅ 调试：打印原始菜单数据
console.log('🔍 Menu.vue 原始菜单数据:', JSON.parse(JSON.stringify(AuthStore.menu)));

// ✅ 修正：确保所有路径都是绝对路径且格式正确
const normalizedMenu = computed(() => {
  return AuthStore.menu.map(item => ({
    ...item,
    path: formatPath(item.path), // 格式化父菜单路径
    children: item.children?.map(child => ({
      ...child,
      path: formatPath(child.path) // 格式化子菜单路径
    }))
  }));
});

// ✅ 工具函数：确保路径以 / 开头
function formatPath(path) {
  if (!path) return '/';
  return path.startsWith('/') ? path : `/${path}`;
}

// ✅ 调试：打印格式化后的数据
console.log('✅ Menu.vue 格式化后菜单:', normalizedMenu.value);
</script>

<template>
  <el-menu 
    :router="true" 
    active-text-color="#0DBC79" 
    background-color="#212222" 
    :default-active="props.defaultActive"  
    text-color="#fff" 
    :collapse="props.isCollapse" 
    :collapse-transition="false"
  >
    <template v-for="menu in normalizedMenu" :key="menu.id">
      <!-- 一级菜单（无子菜单） -->
      <el-tooltip v-if="!menu.children && props.isCollapse" :content="menu.text" placement="right">
        <el-menu-item :index="menu.path">
          <el-icon>
            <SvgIcon :name="menu.icon" width="16px" height="16px" filter="grayscale(1) brightness(2)" />
          </el-icon>
          <span>{{ menu.text }}</span>
        </el-menu-item>
      </el-tooltip>
      
      <el-menu-item v-else-if="!menu.children" :index="menu.path">
        <el-icon>
          <SvgIcon :name="menu.icon" width="16px" height="16px" filter="grayscale(1) brightness(2)" />
        </el-icon>
        <span>{{ menu.text }}</span>
      </el-menu-item>

      <!-- 二级菜单 -->
      <el-sub-menu v-else :index="menu.path">
        <template #title>
          <el-icon>
            <SvgIcon :name="menu.icon" width="16px" height="16px" filter="grayscale(1) brightness(2)" />
          </el-icon>
          <span>{{ menu.text }}</span>
        </template>
        
        <template v-for="child in menu.children" :key="child.id">
          <el-tooltip v-if="props.isCollapse" :content="child.text" placement="right">
            <el-menu-item :index="child.path">
              <el-icon>
                <SvgIcon :name="child.icon" width="16px" height="16px" filter="grayscale(1) brightness(2)" />
              </el-icon>
              <span>{{ child.text }}</span>
            </el-menu-item>
          </el-tooltip>
          
          <el-menu-item v-else :index="child.path">
            <el-icon>
              <SvgIcon :name="child.icon" width="16px" height="16px" filter="grayscale(1) brightness(2)" />
            </el-icon>
            <span>{{ child.text }}</span>
          </el-menu-item>
        </template>
      </el-sub-menu>
    </template>
  </el-menu>
</template>

<style scoped>
.el-menu-item.is-active {}
.el-menu { border-right: none; }
</style>