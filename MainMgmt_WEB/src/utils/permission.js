import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'


/**
 * ① 老函数：带权限校验 + 无权限弹窗
 * @param {string} permission  权限标识，如 'user:delete'
 * @param {Function} callback  通过校验后执行的回调
 */
export const withPerm = (permission, callback) => {
  const authStore = useAuthStore()
  if (authStore.permissions.includes(permission)) {
    callback()
  } else {
    ElMessage.error('您没有该操作的权限')
  }
}
// ------------------------------------------------------------------------------------
// ① 模块级缓存
let permsCache = null
/**
 * 只返回权限数组，不弹窗、不回调
 * 第一次会把 Pinia 数据缓存下来，后续直接读缓存
 */
export function getPerms() {
    // 如果已有缓存，直接返回  
    if (permsCache !== null) return permsCache

    // 第一次：真正去 store 里拿
    const authStore = useAuthStore()
    permsCache = authStore.permissions || []
    // 保留原来的调试日志（只打一次）
    console.log('当前用户权限-1105：', permsCache)
    return permsCache
}

/**
 * 如果登录后权限有变动，手动清一下缓存即可
 */
// ----------------------------------------------------------------------------------------------
/**
 * 真正的权限判断逻辑
 * @param {HTMLElement} el 当前绑定的 DOM 元素
 * @param {Object} binding Vue 指令的 binding 对象，binding.value 就是 v-permission="xxx" 里传的内容
 */
function checkPermission(el, binding) { 
  const { value } = binding;
  const authStore = useAuthStore();        // ✅ 拿到 store 实例
  const permissions = authStore.permissions || [];  // ✅ 直接读属性

  // 情况 1：传入的是数组 ["user:add","user:edit"] —— 满足任意一项就通过
  if (value && Array.isArray(value)) {
    const has = value.some(p => permissions.includes(p)) // 只要有一个存在就返回 true
    if (!has) el.parentNode?.removeChild(el)           // 没权限：直接把元素从 DOM 里删掉
  }
  // 情况 2：传入的是单个字符串 "user:delete"
  else if (value && typeof value === 'string') {
    if (!permissions.includes(value)) el.parentNode?.removeChild(el) // 没权限同样删节点
  }
}

// 导出 Vue 自定义指令对象
export default {
  // 元素第一次挂载到页面时执行
  mounted(el, binding) {
    checkPermission(el, binding)
  },
  // 元素更新（例如绑定值变化）时再执行一次，保证实时生效
  updated(el, binding) {
    checkPermission(el, binding)
  }
}
// 具名导出，让 main.js 可以按 { permission } 引入
export const permission = checkPermission;