import http from "./http"
import axios from 'axios'; 
import { useAuthStore } from "@/stores/auth";
import { ElMessage } from 'element-plus'

// 加拦截器
const instance = axios.create({
  baseURL: import.meta.env.VITE_BASE_URL,
  timeout: 10000
})

// 响应拦截器统一处理错误
instance.interceptors.response.use(
  response => response,
  error => {
    const { response } = error
    
    if (response?.status === 400) {
      // 提取后端返回的详细错误信息
      const detail = response.data?.detail || response.data?.message || '请求参数错误'
      
      // 针对IP重复错误做特殊处理（更友好的提示）
      if (typeof detail === 'string' && detail.includes('该IP地址已存在')) {
        // 直接从错误信息中提取IP
        // 格式: "192.168.1.1 --> 该IP地址已存在!"
        const ipMatch = detail.match(/^([\d.]+) -->/)
        const ip = ipMatch ? ipMatch[1] : '该IP'
        
        // 显示高亮提示，5秒后自动关闭
        ElMessage({
          message: `❌ ${ip} 已被使用，请更换其他IP地址`,
          type: 'error',
          duration: 5000,
          showClose: true,
          customClass: 'error-message-ip-duplicate'
        })
        
        // 返回结构化错误，便于调用方处理
        return Promise.reject({
          status: 400,
          type: 'DUPLICATE_IP',
          ip: ip,
          message: `${ip} 已被使用`,
          originalMessage: detail
        })
      }
      
      // 其他400错误（如字段验证失败）
      if (typeof detail === 'object') {
        const messages = Object.values(detail).flat()
        ElMessage.error(messages.join('；') || '参数验证失败')
      } else {
        ElMessage.error(detail)
      }
      
      return Promise.reject({
        status: 400,
        message: detail,
        data: response.data
      })
    }
    
    // 其他状态码处理...
    if (response?.status === 401) {
      ElMessage.error('登录已过期，请重新登录')
      // 清除token并跳转登录页
      // authStore.clearToken()
      // router.push('/login')
    } else if (response?.status === 403) {
      ElMessage.error('权限不足，无法执行此操作')
    } else if (response?.status === 500) {
      ElMessage.error('服务器错误，请联系管理员')
    } else if (error.message?.includes('timeout')) {
      ElMessage.error('请求超时，请检查网络')
    } else {
      ElMessage.error(error.message || '请求失败')
    }
    
    return Promise.reject(error)
  }
)

const BASE_PATH = "/api/devicemgmt"
// 获取设备列表
const getDeviceinfoList = (page, size, params = {}) => {
    params.page = page
    params.size = size
    return http.get(BASE_PATH + '/devices', params)  // GET /api/devicemgmt/devices
}

// 获取设备详情
const getDeviceDetail = (pk) => {
    return http.get(`${BASE_PATH}/devices/${pk}`)  // GET /api/devicemgmt/devices/8
}

// 添加设备信息
const addDeviceinfo = (data) => {
    return http.post(BASE_PATH + '/devices', data)  // POST /api/devicemgmt/devices
}

// 编辑设备信息
const editDeviceinfo = (pk, deviceInfo) => {
    return http.patch(`${BASE_PATH}/devices/${pk}`, deviceInfo)  // PATCH /api/devicemgmt/devices/8
}

// 删除设备信息
const deleteDeviceinfo = (pk) => {
    return http.delete(`${BASE_PATH}/devices/${pk}`)  // DELETE /api/devicemgmt/devices/8
}

// 获取设备类型
const getDeviceType = () => {
    return http.get(`${BASE_PATH}/device-types`)  // 移除末尾 /
}

// 获取子网类型
const getSubnetType = () => {
    return http.get(`${BASE_PATH}/subnet-types`)  // 移除末尾 /
}

// 解密密码
const getDecodePwd = (pwd) => {
    return http.post(`${BASE_PATH}/decrypt-password`, { decrypt_pwd: pwd })  // 移除末尾 /
}

// 下载设备信息
// ✅ 方案：使用原生 axios，确保 responseType 生效
// ✅ 修改：downloadDeviceinfos 接收 token 参数
// 在 devicemgmtHttp.js 中
const downloadDeviceinfos = (token, pks = []) => {
    const config = {
        method: 'GET',
        url: `${BASE_PATH}/devices/export`,
        responseType: 'blob',
        headers: {
            'Authorization': `Bearer ${token}`,            
        }
    };
    
    // 只在有选中设备时添加参数
    if (pks.length > 0) {
        config.params = { pks: JSON.stringify(pks) };
    }
    
    return axios(config);
}

// ✅ 批量上传设备（必须添加）
const uploadDeviceinfo = (formData) => {
    return http.post(`${BASE_PATH}/upload`, formData, {
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    })
}

export default {
    getDeviceinfoList,
    getDeviceDetail,
    addDeviceinfo,
    editDeviceinfo,
    deleteDeviceinfo,
    getDeviceType,
    getSubnetType,
    getDecodePwd,
    downloadDeviceinfos,
    uploadDeviceinfo,
}