<script setup>
import { ref, watchEffect } from "vue";
import { useRoute } from "vue-router";
import { useAuthStore } from "@/stores/auth"; // 假设你的 Pinia Store 放在 @/stores/auth
import 'animate.css';
import { useThemeStore } from '@/stores/theme';

const themeStore = useThemeStore();

const breadcrumbItems = ref([]);
const route = useRoute();
const authStore = useAuthStore(); // 使用 useAuthStore

// 递归查找菜单项的函数
const findMenuItemByName = (menuList, name) => {
  for (const menuItem of menuList) {
    if (menuItem.name === name) {
      return menuItem;
    }
    if (menuItem.children && menuItem.children.length > 0) {
      const childMatch = findMenuItemByName(menuItem.children, name);
      if (childMatch) {
        return childMatch;
      }
    }
  }
  return null;
};

// 监听路由变化，更新面包屑
watchEffect(() => {
  const matchedRoutes = route.matched;
  const menu = authStore.menu; // 从 authStore 获取菜单项

  // 手动添加“首页”作为第一个面包屑项
  const homeItem = {
    route: {
      name: 'home',
      path: '/',
    },
    text: menu.find(item => item.name === 'home')?.text || '主页', // 从菜单里找“主页”名称
  };

  // 生成面包屑项，过滤掉根路径 '/' 和 frame，同时避免重复添加“首页”
  breadcrumbItems.value = [homeItem, ...matchedRoutes.filter(r => r.name !== 'frame' && r.name !== 'home').map(route => {
    const hasChildren = route.children && route.children.length > 0;
    const isCurrentRoute = route.path === route.fullPath;

    // 递归查找 menu 中匹配的项
    const menuItem = findMenuItemByName(menu, route.name);
    return {
      route: (!hasChildren || isCurrentRoute) ? { name: route.name, params: route.params } : null,
      text: menuItem?.text || route.meta.text || route.name, // 优先从 menu 获取 text，找不到再用 meta.text 或 route.name
    };
  })];
});
</script>

<template>
  <el-breadcrumb class="breadcrumb-container">
    <el-breadcrumb-item v-for="item in breadcrumbItems" :key="item.text" class="slide-in-right">
      <span :class="['router-link-active', themeStore.theme]" v-if="!item.route">{{ item.text }}</span>
      <router-link v-else :to="item.route" :class="['router-link-active', themeStore.theme]">{{ item.text }}</router-link>
    </el-breadcrumb-item>
  </el-breadcrumb>
</template>

<style scoped>

.breadcrumb-container {
  flex: 1;
  display: flex;
  justify-content: flex-start;
  align-items: center;
  padding-left: 20px;
}


/* 从右滑动效果 */
@keyframes slideInRightCustom {
  0% {
    transform: translateX(30%);
    opacity: 0;
  }
  100% {
    transform: translateX(0);
    opacity: 1;
  }
}

.slide-in-right {
  animation: slideInRightCustom 0.5s ease-out forwards;
}
</style>
