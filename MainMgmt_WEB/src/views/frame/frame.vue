<template>
  <!-- 布局容器 -->
  <!-- 导航栏 -->
  <el-container :class="['container', themeStore.theme]" >
    <el-aside  class="aside scrollbar-dark-theme" :width="asideWidth" >
      <!-- 首页 -->
      <router-link to="/" class="brand">
        <img src="/favicon.ico" class="brand-icon" />
        <strong v-show="!isCollapse" style="color: #4fc08d">维护管理</strong>
      </router-link>
      <!-- 菜单栏 -->
      <Menu :isCollapse="isCollapse" :defaultActive="defaultActive"></Menu>
    </el-aside>
    <el-container>
      <!-- 头部 -->
      <el-header class="scrollbar-default" :class="['header',themeStore.theme]">
        <div class="left-header">
          <!-- 展开 -->
          <el-button plain v-show="isCollapse" icon="Expand" @click="onCollapseAside" class="icon-copy"
            style="font-size: 20px" />
          <!-- 收缩 -->
          <el-button plain v-show="!isCollapse" icon="Fold" @click="onCollapseAside" class="icon-copy"
            style="font-size: 20px" />
        </div>
        <!-- 面包屑 -->
          <Breadcrumb />

        <!-- 头像框 -->
        <Avatar />
      </el-header>
      <!-- 主内容 -->
      <el-main class="el-main">
        <!-- tab页 -->
        <GlobalTabs />
        <div class="opsmain">
          <router-view v-slot="{ Component }">
            <transition enter-active-class="animate__animated animate__fadeInLeft10">
              <component :is="Component" />
            </transition>
          </router-view>
        </div>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup name="frame">
    import { ref, computed, watchEffect, onMounted } from 'vue';
    import { useRoute, useRouter } from 'vue-router';
    import GlobalTabs from './com/GlobalTabs.vue';
    import Breadcrumb from './com/Breadcrumb.vue'; // 引入面包屑组件
    import bus from '@/stores/bus'; // 导入事件总线
    import Avatar from './com/avatar.vue';
    import Menu from './com/Menu.vue';


    import { useThemeStore } from '@/stores/theme';
    const themeStore = useThemeStore();


    const router = useRouter(); // 路由跳转
    const route = useRoute(); // 当前路由

    //导航栏-默认选中
    let defaultActive = ref('home');

    // 导航栏-折叠默认属性
    let isCollapse = ref(false);

    // 从 localStorage 中恢复 isCollapse 状态
    const savedIsCollapse = localStorage.getItem('isCollapse');
    if (savedIsCollapse !== null) {
      isCollapse.value = JSON.parse(savedIsCollapse);
    }

    onMounted(() => {
      defaultActive.value = router.currentRoute.value.name; // 处理导航栏菜单默认选中
    });

    // 监听路由变化，更新导航栏选中状态
    watchEffect(() => {
      defaultActive.value = route.name;
    });

    //导航栏-收缩按钮控制
    const onCollapseAside = () => {
      isCollapse.value = !isCollapse.value;

      // 保存 isCollapse 状态到 localStorage
      localStorage.setItem('isCollapse', JSON.stringify(isCollapse.value));

      //事件总线，与子组件通信
      bus.emit('collapseChange', isCollapse.value);
    };

    // 导航栏-折叠宽度,根据折叠变量调整
    let asideWidth = computed(() => {
      return isCollapse.value ? '64px' : '250px';
    });
</script>

<style scoped>
/* 大容器背景颜色 */
.container {
  height: 100vh;
  /* transition: background-color 0.3s ease; */
}

.aside {
  background-color: #212222;
  
  /* 使用 steps 函数创建分阶段动画 */
  transition: 
    width 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94),
    opacity 0.2s ease-in-out 0.1s, /* 延迟开始 */
    transform 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  
  transform: translateX(0) scale(1);
  opacity: 1;
}




.aside .brand {
  color: #fff;
  text-decoration: none;
  /* border-bottom: 1px solid #ac0f8a; */
  background-color: #212222;
  height: 60px;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 20px;
}

.header {
  height: 50px;

  display: flex;
  justify-content: space-between;
  align-items: center;
}


.left-header {
  display: flex;
  align-items: center;
}

/* 头部伸缩按钮控制 */
.el-button+.el-button {
  margin-left: 1px;
}

.el-main {
  --el-main-padding: 0px;
  /* padding-right: 0px;
    padding-left: 20px;  */
  flex: 1;
  /* 确保主内容区域占据剩余空间 */
}

.opsmain {
  /* --el-main-padding: 0px; */
  padding-right: 20px;
  padding-left: 20px;
  /* flex: 1;  */
}

.el-tabs__header {
  margin: 0 0 0px;
  padding: 0;
  position: relative;
}

.brand-icon {
  width: 35px;
  height: 35px;
  margin-right: 5px;
  /* 调整图标与文字的间距 */
}

@keyframes fadeInLeft10 {
  from {
    opacity: 0;
    transform: translateX(-3%);
    /* 只滑动10% */
  }

  to {
    opacity: 1;
    transform: translateX(0);
    /* 到正常位置 */
  }
}

.animate__fadeInLeft10 {
  animation-name: fadeInLeft10;
  animation-duration: 0.5s;
  /* 动画持续时间0.5秒 */
}
</style>
