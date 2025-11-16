<template>
  <div class="alert-history-container">


    <!-- 统计卡片 -->
    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-icon warning">
          <el-icon><Warning /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ alertCount }}</div>
          <div class="stat-label">告警中</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon success">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ resolvedCount }}</div>
          <div class="stat-label">已恢复</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon info">
          <el-icon><DataLine /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ totalCount }}</div>
          <div class="stat-label">总记录</div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { ElMessage } from 'element-plus';
import { Bell, Refresh, Warning, CircleCheck, DataLine, Clock, Message, Monitor } from '@element-plus/icons-vue';
import alarmHttp from '@/api/alertHttp';

// 响应式数据
const loading = ref(false);
const alertList = ref([]);
const totalCount = ref(0);

// 计算属性
const alertCount = computed(() => {
  return alertList.value.filter((alert) => alert.alert_status_display === '告警').length;
});

const resolvedCount = computed(() => {
  return alertList.value.filter((alert) => alert.alert_status_display === '恢复').length;
});

// 获取告警数据
const fetchAlertData = async () => {
  loading.value = true;
  try {
    const response = await alarmHttp.alarmHisInfo();
    alertList.value = response.results || [];
    totalCount.value = response.count || 0;
  } catch (error) {
    ElMessage.error('获取告警数据失败');
    console.error('Error fetching alert data:', error);
  } finally {
    loading.value = false;
  }
};



// 组件挂载时获取数据
onMounted(() => {
  fetchAlertData();
});
</script>

<style scoped>

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.stat-icon.warning {
  background: #fef3c7;
  color: #f59e0b;
}

.stat-icon.success {
  background: #d1fae5;
  color: #10b981;
}

.stat-icon.info {
  background: #dbeafe;
  color: #3b82f6;
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: #6b7280;
  margin-top: 4px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .alert-history-container {
    padding: 16px;
  }

  .stats-cards {
    grid-template-columns: 1fr;
  }
}
</style>
卡片