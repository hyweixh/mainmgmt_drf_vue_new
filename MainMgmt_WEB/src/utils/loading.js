// src/utils/loading.js
import { ElLoading } from 'element-plus'

let loadingInstance

export function showLoading(text = '加载中...') {
  if (loadingInstance) loadingInstance.close()
  loadingInstance = ElLoading.service({ lock: true, text, background: 'rgba(0,0,0,0.7)' })
}

export function hideLoading() {
  loadingInstance?.close()
  loadingInstance = null
}