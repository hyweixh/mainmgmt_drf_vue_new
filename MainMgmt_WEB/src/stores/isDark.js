// useDarkMode.js
import { ref, watch } from 'vue';
import { useThemeStore } from '@/stores/theme';

export function useDarkMode() {
  const themeStore = useThemeStore();
  
  // 初始化 isDark
  const isDark = ref(themeStore.theme === 'dark');
  
  // 监听 themeStore.theme 的变化，自动更新 isDark
  watch(() => themeStore.theme, (newTheme) => {
    isDark.value = newTheme === 'dark';
  });

  return { isDark };
}
