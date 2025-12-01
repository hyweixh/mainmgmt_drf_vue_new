<template>
  <div>
    <!-- 操作区域：修复了缺少 <el-row> 的问题 -->
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
            {{ taskRunning ? '执行中...' : '开始批量Ping检测' }}
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
            placeholder="搜索桩号/设备名称/IP"
            clearable
            size="large"
            @keyup.enter="handleSearch"
          >
            <template #append>
              <el-button @click="handleSearch" icon="Search" />
            </template>
          </el-input>
        </el-col>
      </el-row>
    </el-card>
    
    <!-- 性能警告提示 -->
    <!-- <el-alert 
      v-if="totalRecords > 1000" 
      title="数据量较大，已启用前端分页优化"
      type="warning" 
      :closable="false"
      show-icon
      style="margin-bottom: 15px"
    /> -->
    
    <!-- 统计卡片：修复了多余的 </el-row> -->
    <!-- <el-card v-if="statistics && resultList.length > 0" style="margin-bottom: 20px">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-statistic title="在线设备" :value="statistics.success" value-style="color: #67C23A"/>
        </el-col>
        <el-col :span="6">
          <el-statistic title="离线设备" :value="statistics.failed || statistics.offline" value-style="color: #F56C6C"/>
        </el-col>
        <el-col :span="6">
          <el-statistic title="成功率" :value="statistics.success_rate" suffix="%"/>
        </el-col>
        <el-col :span="6">
          <el-statistic title="总设备数" :value="statistics.total || resultList.length"/>
        </el-col>
      </el-row>
    </el-card>
     -->
    <!-- 表格区域：移除了错误的 <el-col> 标签 -->
    <el-table 
      v-if="resultList.length > 0"
      :data="pagedResultList" 
      height="850" 
      v-loading="taskRunning || loadingHistory"
      style="margin-top: 20px"
      border
      stripe
    >
      <el-table-column prop="position" label="桩号" width="120" fixed show-overflow-tooltip/>
      <el-table-column prop="devicename" label="设备名称" min-width="120" show-overflow-tooltip/>
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
    </el-table>   
    
    <!-- 大数据量统计信息 -->
    <!-- <div v-if="totalRecords > 1000" style="margin-top: 20px; text-align: right;">
      <el-tag type="info">当前显示 {{ (currentPage - 1) * pageSize + 1 }} - {{ Math.min(currentPage * pageSize, totalRecords) }} / {{ totalRecords }} 条</el-tag>
    </div> -->
    
    <!-- 分页组件 -->
    <!-- 分页组件（已修改为左对齐） -->
    <div class="pagination-container" v-if="totalRecords > 0" style="margin-top: 20px;">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="totalRecords"
        :page-sizes="[15, 50, 100, 200]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handlePageSizeChange"
        @current-change="handlePageChange"
      />
      <!-- 统计文字 -->
      <el-tag v-if="totalRecords > 1000" type="info" class="page-stats-tag">
        当前显示 {{ (currentPage - 1) * pageSize + 1 }} - 
        {{ Math.min(currentPage * pageSize, totalRecords) }} / 
        {{ totalRecords }} 条
      </el-tag>
    </div>
    
    <!-- 空状态 -->
    <el-empty 
      v-if="!taskRunning && !loadingHistory && resultList.length === 0" 
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
      @close="errorMsg = ''"
    />
  </div>
</template>


<script setup>
// ==================== 导入 ====================
import { ref, onUnmounted, computed, watch, onMounted } from 'vue'
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

// ✅ 分页状态（用于前端分页）
const currentPage = ref(1)
const pageSize = ref(15)

// ==================== 计算属性 ====================
const currentInspector = computed(() => {
  return authStore.user?.realname || 'system'
})

const totalRecords = computed(() => resultList.value.length)

// 前端搜索过滤
const filteredResultList = computed(() => {
  if (!searchKeyword.value.trim()) {
    return resultList.value
  }
  
  const keyword = searchKeyword.value.toLowerCase()
  return resultList.value.filter(item => 
    item.position?.toLowerCase().includes(keyword) ||
    item.devicename?.toLowerCase().includes(keyword) ||
    item.deviceip?.toLowerCase().includes(keyword)
  )
})

// 前端分页
const pagedResultList = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredResultList.value.slice(start, end)
})

// ==================== 生命周期 ====================
onMounted(() => {
  console.log('🚀 组件挂载，自动加载历史数据...')
  loadHistoricalResults()
})

onUnmounted(() => {
  console.log('🧹 组件卸载，清理资源')
  cleanup()
})

// ==================== 监听 ====================
watch(filteredResultList, (newList) => {
  currentPage.value = 1  // 搜索后重置到第一页
}, { immediate: true })

// ==================== 工具函数 ====================
function formatDateTime(dateStr) {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  const pad = (n) => String(n).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`
}

function getDeviceTypeName(devicetype) {
  if (!devicetype) return '未知'
  
  if (typeof devicetype === 'object') {
    return devicetype.devicetypename || devicetype.name || '未知'
  }
  
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
}

// ==================== 分页处理 ====================
function handlePageSizeChange(newSize) {
  pageSize.value = newSize
  currentPage.value = 1
}

function handlePageChange(newPage) {
  currentPage.value = newPage
}

function handleSearch() {
  // 搜索已在前端计算属性中处理
  currentPage.value = 1
}

function handleSearchClear() {
  searchKeyword.value = ''
  loadHistoricalResults()
}

// ==================== 数据加载 ====================
async function loadHistoricalResults() {
  if (loadingHistory.value) return
  
  loadingHistory.value = true
  errorMsg.value = ''
  
  try {
    console.log('📡 加载历史检查数据...')
    
    const response = await pingdevicesHttp.getHistoricalResults()
    
    if (response?.results) {
      resultList.value = response.results
      statistics.value = calculateStatistics(response.results)
      
      const msg = `已加载 ${response.results.length} 条历史记录`
      if (response.warning) {
        ElMessage.warning(`${msg} - ${response.warning}`)
      } else {
        ElMessage.success(msg)
      }
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

// ... 保留其余批量Ping相关函数（startBatchPing, queryProgressOnce, processResults, saveResultsToDatabase）...
</script>

<style scoped>
.pagination-container {
  display: flex;
  justify-content: flex-start;  /* 从 flex-end 改为 flex-start */
  margin-top: 20px;
}
/* ✅ 自定义标签样式 */
.page-stats-tag {
  font-size: 16px;
  height: auto;
  line-height: 1.5;
  padding: 8px 15px;
  margin-left: 10px;  /* ✅ 距离分页控件10px */
}
</style>