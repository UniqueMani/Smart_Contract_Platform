import axios from 'axios'
import { useAuthStore } from '../store/auth'

const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || 'http://localhost:8000/api',
})

http.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.token) {
    config.headers.Authorization = `Bearer ${auth.token}`
  }
  return config
})

// 响应拦截器：统一处理响应和错误
http.interceptors.response.use(
  (response) => {
    // 对于 2xx 状态码，直接返回响应
    return response
  },
  (error) => {
    // 对于 4xx/5xx 状态码，保留原始错误对象，但添加友好的错误消息
    if (error.response) {
      // 服务器返回了错误响应
      const message = error.response.data?.detail || error.response.data?.message || '请求失败'
      // 保留原始错误对象，添加 message 属性
      error.message = message
      return Promise.reject(error)
    } else if (error.request) {
      // 请求已发出但没有收到响应（网络错误或服务器未运行）
      error.message = '网络错误，请检查网络连接'
      return Promise.reject(error)
    } else {
      // 其他错误，保留原样
      return Promise.reject(error)
    }
  }
)

export default http
