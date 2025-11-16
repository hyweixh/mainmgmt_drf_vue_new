// 适用于totp视图管理
import { ref, watch } from "vue";
import { defineStore } from "pinia";

// 定义 localStorage 键名
const VIEW_KEY = "VIEW_KEY"; // 用于存储 view 的 localStorage 键

export const useViewStore = defineStore("view", () => {
  // 初始化 view 状态，优先从 localStorage 获取值
  const view = ref(parseInt(localStorage.getItem(VIEW_KEY)) || 1); // 默认为 1

  // 将 view 状态保存到 localStorage
  const saveToLocalStorage = () => {
    localStorage.setItem(VIEW_KEY, view.value.toString());
  };

  // 监听 view 状态的变化，并将其保存到 localStorage
  watch(view, saveToLocalStorage);

  // 返回 store 中的状态和方法
  return {
    view,
    setView(newView) {
      view.value = newView;
    },
  };
});
