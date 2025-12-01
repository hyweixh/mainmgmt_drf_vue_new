<template>
  <div>
    <!-- 操作区域：显示当前检查人员 + 执行按钮 -->
    <el-row :gutter="20" style="margin-bottom: 20px">
      <!-- <el-col :span="12">
        <el-alert 
          :title="`当前检查人员：${currentInspector}`" 
          type="info" 
          :closable="false"
        />
      </el-col> -->
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
    </el-row>
    
    <!-- 统计卡片 -->
    <el-row v-if="statistics" :gutter="20" style="margin-top: 20px">
      <el-col :span="6">
        <el-statistic title="在线设备" :value="statistics.success" value-style="color: #67C23A"/>
      </el-col>
      <el-col :span="6">
        <el-statistic title="离线设备" :value="statistics.failed || statistics.error" value-style="color: #F56C6C"/>
      </el-col>
      <el-col :span="6">
        <el-statistic title="成功率" :value="statistics.success_rate" suffix="%"/>
      </el-col>
      <el-col :span="6">
        <el-statistic title="总设备数" :value="statistics.total || resultList.length"/>
      </el-col>
    </el-row>
    
    <!-- 结果表格：完全匹配models.py字段结构 -->
    <el-table 
      :data="resultList" 
      height="600" 
      v-loading="taskRunning"
      style="margin-top: 20px"
      v-if="resultList.length > 0"
      border
      stripe
    >
      <el-table-column prop="position" label="桩号" width="120" fixed show-overflow-tooltip/>
      <el-table-column prop="devicename" label="设备名称" min-width="150" show-overflow-tooltip/>
      <el-table-column prop="deviceip" label="设备IP" width="140"/>
      <el-table-column label="设备类型" width="120">
        <template #default="{ row }">
          <span>{{ getDeviceTypeName(row.devicetype) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="检查结果" width="100" fixed="right">
        <template #default="{ row }">
          <el-tag :type="row.inspectresult === 'online' ? 'success' : 'danger'">
            {{ getResultText(row.inspectresult) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="inspector" label="检查人员" width="100"/>
      <el-table-column label="检查时间" width="160">
        <template #default="{ row }">
          {{ row.inspecttime ? formatDateTime(row.inspecttime) : '-' }}
        </template>
      </el-table-column>
      <el-table-column label="响应时间(ms)" width="120">
        <template #default="{ row }">
          <span v-if="row.response_time !== null">{{ row.response_time }} ms</span>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column prop="error_desc" label="故障描述" min-width="150" show-overflow-tooltip/>
      <el-table-column prop="error_proc" label="故障处理" min-width="150" show-overflow-tooltip/>
      <el-table-column prop="task_id" label="任务ID" width="180" show-overflow-tooltip/>
    </el-table>
    
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
      style="margin-top: 15px;"
    />
  </div>
</template>

<script setup>
// ==================== 导入 ====================
import { ref, onUnmounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'  // ✅ 导入 Pinia store
import pingdevicesHttp from '@/api/pingdevicesHttp'
import { ElMessage } from 'element-plus'
import { showLoading, hideLoading } from '@/utils/loading';

// ==================== 状态管理 ====================
const authStore = useAuthStore()  // ✅ 使用 Pinia store
const taskRunning = ref(false)
const statistics = ref(null)
const resultList = ref([])
const errorMsg = ref('')
const pollInterval = ref(null)

// ==================== 计算属性：当前登录用户 ====================
const currentInspector = computed(() => {
  return authStore.user?.realname || 'system'  // ✅ 从 Pinia 获取用户名
})

// ==================== 轮询配置 ====================
const POLL_INTERVAL_MS = 500
const MAX_DURATION_MS = 60000

// ==================== 生命周期 ====================
onUnmounted(() => {
  console.log('🧹 组件卸载，清理资源')
  cleanup()
})

// ==================== 工具函数 ====================
function formatDateTime(dateStr) {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  const pad = (n) => String(n).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`
}

function getDeviceTypeName(devicetype) {
  if (!devicetype) return '未知'
  return devicetype.name || devicetype || '未知'
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
}

// ==================== 核心功能 ====================
async function startBatchPing() {
  if (!currentInspector.value || currentInspector.value === 'system') {
    ElMessage.warning('无法获取当前用户信息，请先登录')
    return
  }
  
  showLoading('正在执行批量Ping检测...')
  taskRunning.value = true
  errorMsg.value = ''
  resultList.value = []
  statistics.value = null
  
  const startTime = Date.now()
  let taskId = null

  try {
    // 1. 获取完整设备信息
    const deviceData = await pingdevicesHttp.getDeviceList()
    if (!deviceData?.items?.length) {
      throw new Error('没有可用的设备数据')
    }

    // 2. 启动Celery任务
    const taskData = await pingdevicesHttp.startBatchPing(deviceData.items)
    if (!taskData?.task_id) {
      throw new Error('后端未返回有效的task_id')
    }
    taskId = taskData.task_id

    // 3. 立即查询一次进度
    await queryProgressOnce(taskId)

    // 4. 启动轮询
    pollInterval.value = setInterval(async () => {
      if (Date.now() - startTime > MAX_DURATION_MS) {
        cleanup()
        errorMsg.value = '任务执行超时（60秒）'
        ElMessage.error(errorMsg.value)
        return
      }

      try {
        const completed = await queryProgressOnce(taskId)
        if (completed) {
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
    errorMsg.value = `启动失败: ${error.response?.data?.error || error.message}`
    ElMessage.error(errorMsg.value)
    cleanup()
  }
}

async function queryProgressOnce(taskId) {
  try {
    const progressData = await pingdevicesHttp.getBatchPingProgress(taskId)
    if (!progressData) return false

    // 更新统计和结果
    if (progressData.statistics) statistics.value = progressData.statistics
    if (progressData.results) {
      resultList.value = processResults(progressData.results, taskId)
    }

    // 检查完成状态
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
  const currentTime = new Date().toISOString()

  // 统一处理三种结果类型
  const processItem = (item, status, errorDesc = '') => ({
    position: item.position || '',
    devicename: item.devicename || '未知设备',
    deviceip: item.deviceip,
    devicetype: item.devicetype || null,
    inspectresult: status,
    inspector: currentInspector.value,  // ✅ 使用 Pinia store 的用户名
    inspecttime: currentTime,
    task_id: taskId,
    error_desc: errorDesc || item.error_message || '',
    error_proc: item.error_proc || '',
    response_time: item.response_time || null
  })

  results.success?.forEach(item => processed.push(processItem(item, 'online')))
  results.timeout?.forEach(item => processed.push(processItem(item, 'offline', '设备无响应（超时）')))
  results.error?.forEach(item => processed.push(processItem(item, 'error', item.error_message)))

  return processed
}


async function saveResultsToDatabase(taskId) {
  if (!resultList.value.length) return
  
  try {
    console.log('💾 正在保存检查结果到数据库...')
    
    const saveData = resultList.value.map(item => ({
      position: item.position || '',
      devicename: item.devicename || '未知设备',
      deviceip: item.deviceip,
      devicetype: item.devicetype?.id || item.devicetype,
      inspectresult: item.inspectresult,
      inspector: item.inspector,
      inspecttime: item.inspecttime,
      response_time: item.response_time,
      error_desc: item.error_desc,
      error_proc: item.error_proc,
      task_id: taskId
    }))

    const result = await pingdevicesHttp.savePingResults({ results: saveData, task_id: taskId })
    
    // ✅ 显示警告信息
    if (result.warning) {
      ElMessage.warning(result.warning)
    }
    
    console.log(`✅ 成功保存 ${result.saved_count} 条记录`)
    ElMessage.success(`检查结果已保存到数据库（共${result.saved_count}条）`)
  } catch (error) {
    console.error('❌ 保存检查结果失败:', error)
    ElMessage.error('保存失败: ' + (error.response?.data?.error || error.message))
  }
}
</script>