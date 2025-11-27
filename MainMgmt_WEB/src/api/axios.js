import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

// 创建带认证的Axios实例
const apiClient = axios.create({
  baseURL: '/api',
  timeout: 30000
})

// 请求拦截器：自动附加JWT Token
apiClient.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.token) {
      // ✅ 确保Token被添加到请求头
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

export default apiClient