import http from './http';

// 登录：统一传 captcha_key + offset_x
const login = (username, password, captcha_key = null, offset_x = null) => {
  const path = '/api/auth/login';
  const data = { username, password };
  //if (captcha_key) data.captcha_key = captcha_key;
  if (offset_x !== null && offset_x !== undefined) data.offset_x = offset_x;
  return http.post(path, data);
};

// 获取滑动验证码
// const getSliderCaptcha = () => {
//   const path = '/api/auth/slider-captcha';
//   return http.get(path);
// };

// const verifySlider = (captcha_key, offset_x) => {
//   const path = '/api/auth/slider-verify';
//   return http.post(path,{captcha_key, offset_x})
// }

//  普通用户修改密码
// const resetPassword = (password_old, pwd1, pwd2) => {
//   const path = '/api/auth/pwd';
//   return http.post(path, { password_old, pwd1, pwd2 });
// };

/* ==================  管理员重置用户密码  ================== */
// 2025-10-21 by wxh
// 管理员重置用户密码
// const adminResetPassword = (userId, newPwd) => {
//   const path = '/api/auth/admin-reset-password';
//   return http.post(path, { user_id: userId, new_password: newPwd });
// };

// 修改/重置密码接口
// const change_password = (userId, newPwd) => {
//   const path = '/api/change_password';
//   return http.post(path, { user_id: userId, new_password: newPwd });
// };

const changePassword = (data) => {
  // data 里可能带：
  // { old_password: 'xxx', new_password: 'yyy' }               // 自己改
  // { user_id: 18, new_password: 'yyy' }                       // 管理员重置
  console.log('[API-----] changePassword called with', data)
  const path = '/api/auth/change_password';
  return http.post(path, data);
};

// 修改联系方式
const resetContact = (telephone, email) => {
  const path = '/api/auth/contact';
  return http.post(path, { telephone, email });
};

// 上传头像
const uploadImage = (avatar) => {
  const path = '/api/auth/uploadImage';
  return http.post(path, avatar);
};

// 查询用户
const getUserInfo = (username, params) => {
  const path = '/api/auth/users';
  params = params ? params : {};
  params['username'] = username;
  return http.get(path, params);
};
// 添加用户
const addUser = (data) => {
  const path = '/api/auth/users';
  return http.post(path, data);
};
// 修改用户
const updateUser = (id, data) => {
  const path = '/api/auth/users/' + id;
  return http.put(path, data);
};
// 删除用户
const DeleteUser = (id) => {
  const path = '/api/auth/users/' + id;
  return http.delete(path);
};

// 查询角色
const getRoleInfo = () => {
  const path = '/api/role/roles';
  return http.get(path);
};
// 添加角色
const addRole = (data) => {
  const path = '/api/role/roles';
  return http.post(path, data);
};
// 修改角色
const updateRole = (id, data) => {
  const path = '/api/role/roles/' + id;
  return http.put(path, data);
};
// 删除角色
const DeleteRole = (id) => {
  const path = '/api/role/roles/' + id;
  return http.delete(path);
};

// 分配角色菜单
const assignMenu = (data) => {
  const path = '/api/role/assign_menu';
  return http.post(path, data);
};

//获取当前角色id所拥有菜单
const getRoleMenu = (roleId) => {
  const path = '/api/role/role_menus/' + roleId;
  return http.get(path);
};

//获取菜单
const getMenu = () => {
  const path = '/api/menu/menus';
  return http.get(path);
};

// 添加菜单
const addMenu = (data) => {
  const path = '/api/menu/menus';
  return http.post(path, data);
};

// 修改菜单
const updateMenu = (id, data) => {
  const path = '/api/menu/menus/' + id;
  return http.put(path, data);
};

// 排序接口
const sortMenu = (parentId, ids) => {
  const path = `/api/menu/menus/${parentId}/sort`;
  return http.put(path, ids);
};

// 删除菜单
const deleteMenu = (id) => {
  const path = '/api/menu/menus/' + id;
  return http.delete(path);
};

//查看权限按钮
const getPermission = (menu_id, page, size, params) => {
  const path = '/api/permission/permissions';
  params = params ? params : {};
  params['menu_id'] = menu_id;
  params['page'] = page;
  params['size'] = size;
  return http.get(path, params);
};

// 添加权限
const addPermission = (data) => {
  const path = '/api/permission/permissions';
  return http.post(path, data);
};

// 修改权限
const updatePermission = (id, data) => {
  const path = '/api/permission/permissions/' + id;
  return http.put(path, data);
};
// 删除权限
const delPermission = (id) => {
  const path = '/api/permission/permissions/' + id;
  return http.delete(path);
};

// 添加角色按钮
const addRolePermission = (data) => {
  const path = '/api/permission/role-permissions';
  return http.post(path, data);
};

// 查询角色权限按钮
const getRolePermission = (role_id, params) => {
  const path = '/api/permission/role-permissions';
  params = params ? params : {};
  params['role_id'] = role_id;
  return http.get(path, params);
};

//导出权限
const permissionExport = () => {
  const path = '/api/permission/permissions/export';
  return http.downloadFile(path);
};

// 审计日志
const requestLog = (start_time, end_time, query, page, size, params) => {
  const path = '/api/auth/request_logs';
  params = params ? params : {};

  params['start_time'] = start_time;
  params['end_time'] = end_time;
  params['query'] = query;
  params['page'] = page;
  params['size'] = size;
  return http.get(path, params);
};


// 导出包含 login 函数的对象
export default {
  login,
  // resetPassword,
  resetContact,
  uploadImage,
  getUserInfo,
  addUser,
  updateUser,
  DeleteUser,
  getRoleInfo,
  addRole,
  updateRole,
  DeleteRole,
  assignMenu,
  getRoleMenu,
  getMenu,
  addMenu,
  updateMenu,
  deleteMenu,
  getPermission,
  addPermission,
  updatePermission,
  addRolePermission,
  getRolePermission,
  delPermission,
  permissionExport,
  requestLog,
  // getSliderCaptcha,
  // verifySlider,
  sortMenu, // 排序
  // adminResetPassword,   // <-- 新增
  changePassword    // 修改/重置密码
};
