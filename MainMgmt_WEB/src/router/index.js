import { createRouter, createWebHashHistory } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import frame_routes from '@/router/frame';
import login_routes from '@/router/login';

const routes = [...frame_routes, ...login_routes];

const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes
});

// ==================== 调试开关 ====================
// 在 .env.development 文件中添加：VITE_DISABLE_AUTH=true
const DISABLE_AUTH = import.meta.env.VITE_DISABLE_AUTH === 'true';
// =================================================

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();

  if (DISABLE_AUTH) return next();

  // 排除登录和激活页面
  if (to.name !== 'staff_activite' && to.name !== 'login') {
    if (!authStore.is_logined) return next({ name: 'login' });
    
    // 权限检查（第一优先级）
    const requiredPermission = to.matched
      .map(r => r.meta?.permission)
      .find(p => p !== undefined);
    
    if (requiredPermission) {
      const permissions = Array.isArray(authStore.permissions) 
        ? authStore.permissions 
        : JSON.parse(authStore.permissions || '[]');
      
      if (!permissions.includes(requiredPermission)) {
        return next({ name: 'Forbidden' });
      }
      return next(); // 权限通过，直接放行
    }

    // ✅ 第二优先级：检查菜单路径（针对没有 meta.permission 的路由）
    const hasMenuPermission = authStore.menu.some((menuItem) => {
      if (menuItem.path === to.path) return true;
      
      // 检查子菜单，支持动态参数
      return menuItem.children?.some((child) => {
        // 跳过 null children
        if (!child || !child.path) return false;
        
        // 将 :id 转换为正则表达式
        const pathPattern = child.path.replace(/:[^/]+/g, '[^/]+');
        const regex = new RegExp(`^${pathPattern}$`);
        return regex.test(to.path);
      });
    });

    if (!hasMenuPermission && to.name !== 'Forbidden' && to.name !== 'usercenter') {
      console.warn('⚠️ 无菜单权限访问:', to.path);
      return next({ name: 'Forbidden' });
    }
  }else {
    console.log('⏭️ 跳过权限检查 (staff_activite 或 login)');
  }

  console.log('✅ 路由守卫结束，正常放行');

  next();
});

export default router;