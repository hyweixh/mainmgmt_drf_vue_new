// stores/theme.js
import { defineStore } from 'pinia';
import { ref } from 'vue';
import { VxeUI } from 'vxe-table'

export const useThemeStore = defineStore('theme', () => {
  const theme = ref('light');

  // 初始化主题
  const initializeTheme = () => {
    const savedTheme = localStorage.getItem('theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    setTheme(savedTheme);
  };

  // 设置主题
  const setTheme = (newTheme) => {
    theme.value = newTheme;
    const html = document.documentElement;
    newTheme === 'dark' ? html.classList.add('dark') : html.classList.remove('dark');
    VxeUI.setTheme(newTheme)  /* 设置VueTable*/
    localStorage.setItem('theme', newTheme);
  };

  // 切换主题
  const toggleTheme = () => {
    setTheme(theme.value === 'dark' ? 'light' : 'dark');
  };

  return {
    theme,
    initializeTheme,
    toggleTheme,
    setTheme
  };
});
