<template>
  <div>
    <!-- 操作区域 -->
    <el-card style="margin-bottom: 20px">
      <el-row :gutter="20" align="middle">
        <el-col :span="6">
          <el-button 
            @click="startBatchPing" 
            :loading="taskRunning"
            type="primary"
            :disabled="taskRunning"
            size="large"
            style="width: 100%"
          >
            {{ taskRunning ? '执行中...' : '开始批量Ping' }}
          </el-button>
        </el-col>

        <el-col :span="6">
          <el-button 
            @click="loadHistoricalResults" 
            :loading="loadingHistory"
            type="info"
            size="large"
            style="width: 100%"
          >
            刷新历史数据
          </el-button>
        </el-col>
        
        <el-col :span="8" :offset="4">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索桩号/设备名称/IP/检测结果"
            clearable
            size="large"
            @keyup.enter="handleSearch"
            @clear="handleSearchClear"
          >
            <template #append>
              <el-button @click="handleSearch" icon="Search" />
            </template>
          </el-input>
        </el-col>
      </el-row>
    </el-card>
    
    <!-- 结果表格 -->
    <el-table 
      :data="pagedResultList" 
      height="850" 
      v-loading="taskRunning || loadingHistory"
      style="margin-top: 20px"
      v-if="resultList.length > 0"
      border
      stripe
    >
      <el-table-column prop="position" label="桩号/位置" width="150" fixed show-overflow-tooltip/>
      <el-table-column prop="devicename" label="设备名称" min-width="80" show-overflow-tooltip/>
      <el-table-column prop="deviceip" label="设备IP" width="150"/>
      
      <!-- ✅ 设备类型列（已修复） -->
      <el-table-column label="设备类型" width="150">
        <template #default="{ row }">
          <span>{{ getDeviceTypeName(row.devicetype) }}</span>
        </template>
      </el-table-column>
      
      <el-table-column label="检查结果" width="120" fixed="right">
        <template #default="{ row }">
          <el-tag :type="row.inspectresult === 'online' ? 'success' : 'danger'">
            {{ getResultText(row.inspectresult) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="inspector" label="检查人员" width="140"/>
      <el-table-column label="检查时间" width="200">
        <template #default="{ row }">
          {{ row.inspecttime ? formatDateTime(row.inspecttime) : '-' }}
        </template>
      </el-table-column>
      <el-table-column label="响应时间(ms)" width="180">
        <template #default="{ row }">
          <span v-if="row.response_time !== null">{{ row.response_time }} ms</span>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column prop="error_desc" label="故障描述" min-width="120" show-overflow-tooltip/>
      <el-table-column prop="error_proc" label="故障处理" min-width="120" show-overflow-tooltip/>
    </el-table>   
    
    <!-- 分页组件 -->
    <div class="pagination-container" v-if="resultList.length > 0" style="margin-top: 20px;">
      <el-pagination
        :key="paginationKey"  
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="totalRecords"
        :page-sizes="[15, 50, 100, 200]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handlePageSizeChange"
        @current-change="handlePageChange"
      />
      <el-tag v-if="totalRecords > 1000" type="info" class="page-stats-tag">
        当前显示 {{ (currentPage - 1) * pageSize + 1 }} - 
        {{ Math.min(currentPage * pageSize, totalRecords) }} / 
        {{ totalRecords }} 条
      </el-tag>
    </div>
    
    <!-- 空状态 -->
    <el-empty 
      v-if="!taskRunning && resultList.length === 0" 
      description="暂无数据，点击按钮开始批量Ping检测" 
      style="margin-top: 50px"
    />
    
    <!-- 错误提示 -->
    <el-alert 
      v-if="errorMsg" 
      :title="errorMsg" 
      type="error" 
      :closable="true" 
      @close="errorMsg = ''"
      style="margin-top: 15px;"
    />
  </div>
</template>

<script setup>
// ==================== 导入 ====================
import { ref, onUnmounted, computed, onMounted, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import pingdevicesHttp from '@/api/pingdevicesHttp'
import { ElMessage } from 'element-plus'
import { showLoading, hideLoading } from '@/utils/loading';

// ==================== 状态管理 ====================
const authStore = useAuthStore()
const taskRunning = ref(false)
const loadingHistory = ref(false)
const statistics = ref(null)
const resultList = ref([])
const errorMsg = ref('')
const pollInterval = ref(null)
const searchKeyword = ref('')

// ✅ 新增：设备类型映射表（键：ID，值：名称）
const deviceTypeMap = ref({})
// 添加检查结果状态映射
const STATUS_MAP = { '在线': 'online', '离线': 'offline', '检查失败': 'error' }

// ✅ 分页状态
const currentPage = ref(1)
const pageSize = ref(15)
const paginationKey = ref(Date.now())  // ✅ 分页组件刷新key

// ✅ 任务完成标志
let taskCompleted = false

// ✅ 关键：普通对象存储设备缓存（避免响应式性能问题）
let deviceMap = {}

// ==================== 计算属性 ====================
const currentInspector = computed(() => {
  return authStore.user?.realname || 'system'
})

// 过滤后的数据列表
const filteredResultList = computed(() => {
  if (!searchKeyword.value.trim()) {
    console.log('📝 无搜索关键词，返回全部数据')
    return resultList.value
  }
  
  const keyword = searchKeyword.value.toLowerCase()
  const reverseStatusMap = {
    'online': '在线',
    'offline': '离线',
    'error': '检查失败'
  }
  
  const filtered = resultList.value.filter(item => {
    const chineseStatus = reverseStatusMap[item.inspectresult] || ''
    
    const match = item.position?.toLowerCase().includes(keyword) ||
                  item.devicename?.toLowerCase().includes(keyword) ||
                  item.deviceip?.toLowerCase().includes(keyword) ||
                  chineseStatus.toLowerCase().includes(keyword)
    
    return match
  })
  
  console.log(`📊 过滤结果: ${resultList.value.length} -> ${filtered.length} 条`)
  return filtered
})

// ✅ 关键修复：分页总记录数必须基于过滤后的数据
const totalRecords = computed(() => {
  const count = filteredResultList.value.length
  console.log('📊 分页统计更新:', {
    原始记录数: resultList.value.length,
    过滤后记录数: count,
    当前关键词: searchKeyword.value
  })
  return count
})

const pagedResultList = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredResultList.value.slice(start, end)
})

// ==================== 轮询配置 ====================
const POLL_INTERVAL_MS = 500
const MAX_DURATION_MS = 60000

// ==================== 生命周期 ====================
onMounted(() => {
  console.log('🚀 组件挂载，自动加载数据...')
  // ✅ 同时加载设备类型和历史数据
  Promise.all([
    loadDeviceTypes(),
    loadHistoricalResults()
  ])
})

onUnmounted(() => {
  console.log('🧹 组件卸载，清理资源')
  cleanup()
})

// ==================== 工具函数 ====================
function getMySQLDateTime() {
  const now = new Date()
  const pad = (n) => String(n).padStart(2, '0')
  return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())} ${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`
}

function formatDateTime(dateStr) {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  const pad = (n) => String(n).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`
}

// ✅ 修改后的函数：支持动态映射和多种格式
function getDeviceTypeName(devicetype) {
  if (!devicetype) return '未知'
  
  // 1. 如果是对象格式（来自原始设备列表）
  if (typeof devicetype === 'object') {
    return devicetype.devicetypename || devicetype.name || '未知'
  }
  
  // 2. 如果是数字或字符串ID（来自缓存或数据库）
  const id = parseInt(devicetype, 10)
  if (!isNaN(id)) {
    return deviceTypeMap.value[id] || `未知类型(${id})`
  }
  
  // 3. 其他情况
  return String(devicetype)
}

function getResultText(result) {
  const map = { 'online': '在线', 'offline': '离线', 'error': '检查失败' }
  return map[result] || '未知'
}

function cleanup() {
  if (pollInterval.value) {
    clearInterval(pollInterval.value)
    pollInterval.value = null
  }
  hideLoading()
  taskRunning.value = false
  loadingHistory.value = false
  taskCompleted = false
}

// ==================== 数据标准化 ====================
function normalizeDeviceType(devicetype) {
  if (!devicetype) return null
  if (typeof devicetype === 'object') return devicetype.id || null
  const id = parseInt(devicetype, 10)
  return isNaN(id) ? null : id
}

// ✅ 最终版：缓存优先 + 设备类型标准化
function normalizeResultItem(item, taskId, status, errorDesc = '') {
  if (!item.deviceip) {
    console.error('❌ 无效的设备数据，缺少deviceip:', item)
    return null
  }

  // 查找缓存（普通对象）
  const cachedDevice = deviceMap[item.deviceip?.trim()] || {}
  
  // 缓存优先于 item 数据
  const devicename = cachedDevice.devicename || 
                     item.devicename || 
                     item.name || 
                     item.device_name || 
                     '未知设备'
  
  const position = cachedDevice.position || item.position || '未知桩号'
  const devicetype = cachedDevice.devicetype || item.devicetype

  return {
    id: item.id || null,
    deviceip: item.deviceip,
    position: position,
    devicename: devicename,
    devicetype: normalizeDeviceType(devicetype),
    inspectresult: status,
    inspector: currentInspector.value,
    inspecttime: getMySQLDateTime(),
    response_time: item.response_time !== undefined ? item.response_time : null,
    error_desc: errorDesc || item.error_message || '',
    error_proc: item.error_proc || '',
    task_id: taskId
  }
}

// ==================== 分页处理 ====================
function handlePageSizeChange(newSize) {
  pageSize.value = newSize
  currentPage.value = 1
  paginationKey.value = Date.now()  // ✅ 强制刷新分页组件
}

function handlePageChange(newPage) {
  currentPage.value = newPage
}

function handleSearch() {
  currentPage.value = 1
  paginationKey.value = Date.now()  // ✅ 强制刷新分页组件
  console.log('🔍 执行搜索，重置到第1页')
}

function handleSearchClear() {
  searchKeyword.value = ''
  currentPage.value = 1
  paginationKey.value = Date.now()  // ✅ 强制刷新分页组件
  loadHistoricalResults()
}

// ==================== 数据加载 ====================
// ✅ 加载设备类型列表
async function loadDeviceTypes() {
  try {
    const response = await pingdevicesHttp.getDeviceTypes()
    
    if (Array.isArray(response) && response.length > 0) {
      const map = {}
      response.forEach((type) => {
        if (type.id) {
          map[type.id] = type.devicetypename || type.name || `类型${type.id}`
        }
      })
      deviceTypeMap.value = map
      console.log('📦 设备类型映射:', map)
    } else {
      console.error('❌ 响应数据格式错误')
    }
  } catch (error) {
    console.error('❌ 加载设备类型失败:', error)
  }
}

async function loadHistoricalResults() {
  if (loadingHistory.value) return
  
  taskCompleted = true
  loadingHistory.value = true
  errorMsg.value = ''
  resultList.value = []
  statistics.value = null
  currentPage.value = 1  // ✅ 加载新数据时重置页码

  try {
    console.log('📡 加载历史检查数据...')
    const response = await pingdevicesHttp.getHistoricalResults()
    
    if (response?.results) {
      const validResults = response.results.filter(item => item.deviceip)
      resultList.value = validResults
      statistics.value = calculateStatistics(validResults)
      
      const msg = `已加载 ${validResults.length} 条历史记录`
      console.log('✅', msg)
      ElMessage.success(msg)
    } else {
      resultList.value = []
      statistics.value = null
    }
    
  } catch (error) {
    console.error('❌ 加载历史数据失败:', error)
    errorMsg.value = `加载历史数据失败: ${error.message}`
    ElMessage.error(errorMsg.value)
  } finally {
    loadingHistory.value = false
    taskCompleted = false
    paginationKey.value = Date.now()  // ✅ 强制刷新分页组件
  }
}

function calculateStatistics(data) {
  if (!data || data.length === 0) return null
  
  const total = data.length
  const success = data.filter(item => item.inspectresult === 'online').length
  const failed = data.filter(item => item.inspectresult === 'offline').length
  const error = data.filter(item => item.inspectresult === 'error').length
  
  return {
    total,
    success,
    failed,
    error,
    success_rate: Math.round((success / total) * 100)
  }
}

// ==================== 核心功能 ====================
async function startBatchPing() {
  if (!currentInspector.value || currentInspector.value === 'system') {
    ElMessage.warning('无法获取当前用户信息，请先登录')
    return
  }
  
  if (taskRunning.value) {
    ElMessage.warning('批量Ping任务正在执行中...')
    return
  }

  showLoading('正在执行批量Ping检测...')
  taskRunning.value = true
  taskCompleted = false
  errorMsg.value = ''
  resultList.value = []
  statistics.value = null
  currentPage.value = 1

  const startTime = Date.now()
  let taskId = null

  try {
    const deviceData = await pingdevicesHttp.getDeviceList()
    console.log('📡 获取设备数量:', deviceData.items.length)
    
    if (!deviceData?.items?.length) {
      throw new Error('没有可用的设备数据')
    }

    // 构建普通对象缓存
    deviceMap = {}
    
    deviceData.items.forEach(device => {
      const ip = device.deviceip?.trim()
      if (ip && !deviceMap[ip]) {
        deviceMap[ip] = {
          position: device.position?.trim() || '未知桩号',
          devicename: device.devicename || device.name || device.device_name || '未知设备',
          devicetype: device.devicetype
        }
      }
    })
    
    console.log('📦 设备缓存已构建，数量:', Object.keys(deviceMap).length)

    const taskData = await pingdevicesHttp.startBatchPing(deviceData.items)
    if (!taskData?.task_id) {
      throw new Error('后端未返回有效的task_id')
    }
    taskId = taskData.task_id
    console.log('🆔 任务ID:', taskId)

    await queryProgressOnce(taskId)

    pollInterval.value = setInterval(async () => {
      if (taskCompleted || Date.now() - startTime > MAX_DURATION_MS) {
        if (Date.now() - startTime > MAX_DURATION_MS) {
          errorMsg.value = '任务执行超时（60秒）'
          ElMessage.error(errorMsg.value)
        }
        cleanup()
        return
      }

      try {
        const completed = await queryProgressOnce(taskId)
        if (completed) {
          taskCompleted = true
          await saveResultsToDatabase(taskId)
          cleanup()
        }
      } catch (error) {
        cleanup()
        errorMsg.value = `获取进度失败: ${error.message}`
        ElMessage.error(errorMsg.value)
      }
    }, POLL_INTERVAL_MS)

  } catch (error) {
    cleanup()
    errorMsg.value = `启动失败: ${error.response?.data?.error || error.message}`
    ElMessage.error(errorMsg.value)
  }
}

async function queryProgressOnce(taskId) {
  try {
    const progressData = await pingdevicesHttp.getBatchPingProgress(taskId)
    if (!progressData) return false

    console.log('📊 进度数据状态:', progressData.state)
    if (progressData.statistics) statistics.value = progressData.statistics
    if (progressData.results) {
      resultList.value = processResults(progressData.results, taskId)
      console.log('✅ 处理后数据样例:', JSON.stringify(resultList.value[0]))
    }

    const isCompleted = ['SUCCESS', 'FAILURE', 'ERROR'].includes(progressData.state)
    
    if (isCompleted) {
      const successCount = statistics.value?.success || 0
      const totalCount = resultList.value.length
      ElMessage.success(`批量Ping完成！在线: ${successCount}/${totalCount}`)
    }
    
    return isCompleted
  } catch (error) {
    console.error('❌ 查询进度失败:', error)
    throw error
  }
}

function processResults(results, taskId) {
  const processed = []
  
  results.success?.forEach(item => {
    const processedItem = normalizeResultItem(item, taskId, 'online')
    if (processedItem) processed.push(processedItem)
  })
  
  results.timeout?.forEach(item => {
    const processedItem = normalizeResultItem(item, taskId, 'offline', '设备无响应（超时）')
    if (processedItem) processed.push(processedItem)
  })
  
  results.error?.forEach(item => {
    const processedItem = normalizeResultItem(item, taskId, 'error', item.error_message)
    if (processedItem) processed.push(processedItem)
  })

  return processed
}

async function saveResultsToDatabase(taskId) {
  if (!resultList.value.length) return
  
  console.log('💾 准备保存，记录数:', resultList.value.length)
  
  try {
    const batchSize = 50
    let totalSaved = 0
    
    for (let i = 0; i < resultList.value.length; i += batchSize) {
      const batch = resultList.value.slice(i, i + batchSize)
      
      const result = await pingdevicesHttp.savePingResults({ 
        results: batch, 
        task_id: taskId 
      })
      
      totalSaved += result.saved_count || 0
    }
    
    ElMessage.success(`检查结果已保存（共${totalSaved}条）`)
  } catch (error) {
    console.error('❌ 保存失败:', error)
    ElMessage.error('保存失败: ' + (error.response?.data?.error || error.message))
  }
}

// ✅ 监听搜索关键词变化
watch(searchKeyword, (newVal) => {
  console.log('🔍 搜索关键词变化:', newVal)
  currentPage.value = 1
  paginationKey.value = Date.now()  // ✅ 强制刷新分页组件
})

</script>

<style scoped>
.pagination-container {
  display: flex;
  justify-content: flex-start;
  margin-top: 20px;
}

.page-stats-tag {
  font-size: 16px;
  height: auto;
  line-height: 1.5;
  padding: 8px 15px;
  margin-left: 10px;
}
</style>