<template>
  <!-- style="border-bottom: 1px solid #e6e6e6;" -->
  <div :class="['global-tabs-header', themeStore.theme]">
    <!-- 标签页 -->
    <div style="width: 98%;margin-top: 2px;">
      <el-tabs v-model="activeTab" type="card" @tab-click="handleTabClick" @tab-remove="handleTabRemove">
        <el-tab-pane v-for="tab in tabs" :key="tab.name" :name="tab.name" :closable="tab.closable">
          <template #label>
            <SvgIcon 
            :name="getIconForTab(tab.name)" width="16px" height="16px" 
            style="margin-right: 5px" 
            :filter="themeStore.theme === 'dark' ? 'grayscale(1) brightness(2)' : ''" 
            />
            <span :class="['tabs-text', themeStore.theme]">{{ getLabelForTab(tab.name) }}</span>
          </template>
        </el-tab-pane>
      </el-tabs>
    </div>
    <!-- 标签操作 -->
    <div>
      <el-dropdown trigger="click">
        <div :class="['tabs-div-button', themeStore.theme]" >
          <el-button :class="['operation-mini-icon',themeStore.theme]" icon="ArrowDownBold" style="width: 10px; "/>
        </div>
        
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item @click="closeLeftTabs" icon="DArrowLeft">关闭左侧</el-dropdown-item>
            <el-dropdown-item @click="closeRightTabs" icon="DArrowRight">关闭右侧</el-dropdown-item>
            <el-dropdown-item divided @click="closeOtherTabs" icon="CircleClose">关闭其他</el-dropdown-item>
            <el-dropdown-item @click="closeAllTabs" icon="DocumentDelete">关闭所有</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useThemeStore } from '@/stores/theme';
const themeStore = useThemeStore();

const router = useRouter();
const route = useRoute();
const AuthStore = useAuthStore();


// 关闭其他标签页，保留当前标签页和主页
const closeOtherTabs = () => {
  const currentIndex = tabs.value.findIndex(tab => tab.name === activeTab.value);
  tabs.value = tabs.value.filter((tab, index) => tab.name === 'home' || index === currentIndex);
  saveTabs();
  console.log("关闭其他标签页");
};


// 关闭所有标签页，保留主页
const closeAllTabs = () => {
  tabs.value = [{ name: 'home', route: '/', closable: false }];
  activeTab.value = 'home';
  router.push('/');
  console.log("关闭所有标签页");
};

// 关闭左侧标签页
const closeLeftTabs = () => {
  const currentIndex = tabs.value.findIndex(tab => tab.name === activeTab.value);
  if (currentIndex > 0) {
    tabs.value.splice(1, currentIndex - 1); // 保留主页（索引0）
    saveTabs();
  }
};

// 关闭右侧标签页
const closeRightTabs = () => {
  const currentIndex = tabs.value.findIndex(tab => tab.name === activeTab.value);
  if (currentIndex < tabs.value.length - 1) {
    tabs.value.splice(currentIndex + 1);
    saveTabs();
  }
};

const tabs = ref([
  { name: 'home', route: '/', closable: false } // 主页为不可关闭标签页
]);
const activeTab = ref('home'); // 默认选中的标签页

// 获取每个标签的名称
const getLabelForTab = (tabName) => {
  if (tabName === 'home') return '主页';
  const menuRoute = findRouteInMenu(tabName);
  return menuRoute ? menuRoute.text : tabName;
};

// 获取每个标签的图标
const getIconForTab = (tabName) => {
  if (tabName === 'home') return 'home';
  const menuRoute = findRouteInMenu(tabName);
  return menuRoute ? menuRoute.icon : '';
};

// 查找菜单中的路由
const findRouteInMenu = (name) => {
  if (name === 'usercenter') {
    return { text: '个人中心', icon: 'people' };
  }
  if (name === 'Forbidden') {
    return { text: '错误页', icon: 'error' };
  }
  const findMenu = (menuItems) => {
    for (const item of menuItems) {
      if (item.name === name) return item;
      if (item.children && item.children.length > 0) {
        const foundChild = findMenu(item.children);
        if (foundChild) return foundChild;
      }
    }
    return null;
  };
  return findMenu(AuthStore.menu);
};

// 恢复标签页状态
const restoreTabs = () => {
  const savedTabs = JSON.parse(localStorage.getItem('tabs')) || [];
  tabs.value = savedTabs.length > 0 ? savedTabs : tabs.value;
  const savedActiveTab = localStorage.getItem('activeTab');
  activeTab.value = savedActiveTab || 'home';
};

// 保存标签页状态
const saveTabs = () => {
  localStorage.setItem('tabs', JSON.stringify(tabs.value));
  localStorage.setItem('activeTab', activeTab.value);
};

// 监听路由变化，更新标签页
watch(
  () => route.name,
  (to) => {
    const existingTab = tabs.value.find((tab) => tab.name === to);
    if (!existingTab) {
      const matchedRoute = findRouteInMenu(to);
      if (matchedRoute) {
        tabs.value.push({ name: to, route: { name: to }, closable: true });
      }
    }
    activeTab.value = to;
    saveTabs(); // 保存状态
  }
);

// 处理标签页移除
const handleTabRemove = (tabName) => {
  const index = tabs.value.findIndex((t) => t.name === tabName);
  if (index !== -1) {
    // 如果当前移除的是当前激活的标签页
    if (activeTab.value === tabName) {
      // 如果移除的是最后一个标签页，则跳转到第一个标签页，否则跳转到上一个标签页
      const nextTab = tabs.value[index > 0 ? index - 1 : 0];
      activeTab.value = nextTab.name;
      router.push(nextTab.route);
    }
    tabs.value.splice(index, 1);
    saveTabs(); // 保存状态
  }
};

// 处理标签点击切换
const handleTabClick = (tabItem) => {
  router.push({ name: tabItem.props.name });
  saveTabs(); // 保存状态
};

// 组件挂载时恢复标签页状态
onMounted(() => {
  restoreTabs();
  const savedActiveTab = localStorage.getItem('activeTab');
  if (savedActiveTab) {
    const activeTabRoute = tabs.value.find((tab) => tab.name === savedActiveTab)?.route;
    if (activeTabRoute) {
      router.push(activeTabRoute);
    }
  }
});
</script>

<style scoped>



.el-tabs__nav-prev::before {
  content: ArrowLeftBold;
  display: inline-block;
  width: 16px;
  height: 16px;
}

/* 标签页下标颜色 */
.el-tabs--card :deep(.el-tabs__item.is-active) {
  border-bottom-color: #626aef;
  border-bottom-width: 2px;
  /* 增加下划线的高度 */
}

:deep(.el-tabs__header) {
  margin: 0;
}

/* 修改标签页的背景颜色和字体颜色 */
:deep(.el-tabs--card .el-tabs__item) {
  /* 字体颜色 */
  color: #606266;
  margin-right: 0px;
  /* 添加标签页之间的间隙 */
  /* 增加标签页的左右内边距 */
  /* padding: 0 15px;   */
  /* 添加圆角 */
  /* border-radius: 4px;  */
  /* 取消边框 */
  border-left: none;
}

/* 取消所有标签页的上边框 */
:deep(.el-tabs--card > .el-tabs__header .el-tabs__nav) {
  border: 0px;
  padding-left: 20px;
}

/* 添加选中的标签页的样式 */
:deep(.el-tabs--card .el-tabs__item.is-active) {
  color: #626aef;
}

.el-tabs {
  /* 标签页高度 */
  --el-tabs-header-height: 28px;
}

.global-tabs-header {
  display: flex;
  justify-content: space-between;
  /* 将子元素左右分开 */
  align-items: center;
  /* 垂直居中 */
}


/* 左移图标 */
:deep(.el-tabs__nav-prev) {
  margin-top: -2px;
  cursor: pointer;
  font-size: 22px;
  line-height: 34px;
  position: absolute;
  text-align: center;
}
/* 右移动图标 */
:deep(.el-tabs__nav-next) {
  margin-top: -2px;
  cursor: pointer;
  font-size: 22px;
  line-height: 34px;
  position: absolute;
  text-align: center;
}
/* 不显示默认下标灰色 */
:deep(.el-tabs__header) {
  border-bottom: none;
}
</style>
