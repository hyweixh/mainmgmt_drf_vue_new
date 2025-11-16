import { ref, computed } from "vue";
import { defineStore } from "pinia";

// 定义 localStorage 键名
const USER_KEY = "USER_KEY";
const TOKEN_KEY = "TOKEN_KEY";
const MENU_KEY = "MENU_KEY";
const PERMISSION_KEY = "PERMISSION_KEY"; // 新增权限键名

export const useAuthStore = defineStore("auth", () => {
  let _user = ref({});
  let _token = ref("");
  let _menu = ref([]);
  let _permissions = ref([]); 

  // 更新 setUserToken 方法，保存 menu
  function setUserToken(user, token, menu,permissions) {
    // 将用户信息、令牌、角色和菜单保存到内存中
    _user.value = user;
    _token.value = token;
    _menu.value = menu;
    _permissions.value = permissions;

    // 将用户信息、令牌、菜单和权限存储到 localStorage 中
    localStorage.setItem(USER_KEY, JSON.stringify(user));
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(MENU_KEY, JSON.stringify(menu));
    localStorage.setItem(PERMISSION_KEY, JSON.stringify(permissions));
  }

  // 计算属性：用户信息
  let user = computed(() => {
    // 如果内存中的用户信息为空，从 localStorage 中读取
    if (Object.keys(_user.value).length === 0) {
      let user_str = localStorage.getItem(USER_KEY);
      if (user_str) {
        _user.value = JSON.parse(user_str);
      }
    }
    return _user.value;
  });

  // 计算属性：令牌
  let token = computed(() => {
    // 如果内存中的令牌为空，从 localStorage 中读取
    if (!_token.value) {
      let token_str = localStorage.getItem(TOKEN_KEY);
      if (token_str) {
        _token.value = token_str;
      }
    }
    return _token.value;
  });


  // 计算属性：菜单信息
  let menu = computed(() => {
    // 如果内存中的菜单为空，从 localStorage 中读取
    if (_menu.value.length === 0) {
      let menu_str = localStorage.getItem(MENU_KEY);
      if (menu_str) {
        _menu.value = JSON.parse(menu_str);
      }
    }
    return _menu.value;
  });

  // 计算属性：权限信息
  let permissions = computed(() => {
    if (_permissions.value.length === 0) {
      let permissions_str = localStorage.getItem(PERMISSION_KEY);
      if (permissions_str) {
        _permissions.value = JSON.parse(permissions_str);
      }
    }
    return _permissions.value || [];
  });

  // 判断是否登录
  let is_logined = computed(() => {
    return Object.keys(user.value).length > 0 && token.value;
  });

  // 删除用户信息、令牌、角色和菜单
  function clearUserToken() {
    _user.value = {};
    _token.value = "";
    _menu.value = [];
    _permissions.value = []; // 清空权限
    localStorage.removeItem(USER_KEY);
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(MENU_KEY);
    localStorage.removeItem(PERMISSION_KEY); // 删除权限
  }

  // 返回给外面访问
  return {
    setUserToken,
    user,
    token,
    menu,
    permissions, // 暴露权限
    is_logined,
    clearUserToken,
  };
});

