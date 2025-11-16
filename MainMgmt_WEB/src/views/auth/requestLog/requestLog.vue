<script setup name="keepalived">
import { ref, onMounted, reactive } from 'vue';
import authHttp from '@/api/authHttp';
import { ElMessage } from 'element-plus';
import timeFormatter from '@/utils/timeFormatter';
import Pagination from '@/components/Pagination.vue';
import { useThemeStore } from '@/stores/theme';

const themeStore = useThemeStore();


// 定义筛选条件
const dateRange = ref([]); // 用于存储时间段，开始时间和结束时间
const message = ref(''); // 日志内容关键字

// 分页参数
let pagination = reactive({
  total: 0, // 分页总数
  page: 1 // 当前页数
});

let page_size = ref(15);

// 更新页码
const updatePage = (newPage) => {
  pagination.page = newPage;
  requestCelerylog(newPage, page_size.value);
};

// 更新条目数
const updatePageSize = (newPageSize) => {
  page_size.value = newPageSize;
  requestCelerylog(pagination.page, newPageSize);
};

// 日志数据
const logs = ref([]);

// 请求日志数据函数
const requestCelerylog = async (page, size) => {
  try {
    // 处理 dateRange 为空的情况
    const start_time = dateRange.value && dateRange.value.length ? dateRange.value[0] : null;
    const end_time = dateRange.value && dateRange.value.length ? dateRange.value[1] : null;

    let data = await authHttp.requestLog(start_time, end_time, message.value, page, size);
    logs.value = data.results;
    pagination.total = data.count;
    pagination.page = page;
  } catch (message) {
    ElMessage.error(message);
  }
};

// 组件挂载时请求数据
onMounted(() => {
  requestCelerylog(pagination.page, page_size.value);
});

// 提交表单查询
const handleSubmit = () => {
  pagination.page = 1; // 新的搜索条件时，重置页码为第一页
  requestCelerylog(pagination.page, page_size.value);
};

const getCodeType = (statusCode) => {
  // 判断状态码的第一个数字
  const firstDigit = String(statusCode)[0];

  // 判断并返回相应的 type
  if (firstDigit === '2') {
    return 'success'; // 2开头的状态码是 success
  } else if (firstDigit === '3') {
    return 'warning'; // 3开头的状态码是 warning
  } else {
    return 'danger'; // 其他状态码是 danger
  }
};

const getTagType = (method) => {
  switch (method) {
    case 'GET':
      return 'success';
    case 'POST':
      return 'warning';
    case 'DELETE':
      return 'danger';
  }
};
</script>

<template>
  <div>
    <!-- 筛选 -->
    <el-card>
      <div class="location-container">
        <el-text>时间范围：</el-text>
        <el-form-item style="width: 25%; margin: 0">
          <el-date-picker
            v-model="dateRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
            @change="handleSubmit"
          />
        </el-form-item>

        <el-text style="margin-left: 2%">关键字：</el-text>
        <el-input v-model="message" placeholder="日志关键字" style="width: 10%" />
        <el-button color="#626aef" type="primary" @click="handleSubmit" style="margin-left: 4px">查询</el-button>
      </div>
    </el-card>

    <!-- 显示日志数据 -->
    <div :class="['table-container', themeStore.theme]">
      <el-table :data="logs" style="width: 100%; height: 75vh">
        <el-table-column type="index" label="序号" align="center" width="60" />
        <el-table-column prop="timestamp" label="时间" width="200" align="center">
          <template v-slot="scope">
            {{ timeFormatter.stringFromDateTime(scope.row.timestamp) }}
          </template>
        </el-table-column>
        <el-table-column prop="client_ip" label="ip地址" align="center" width="150" />
        <el-table-column prop="user_info" label="操作用户" align="center" width="150" />
        <el-table-column prop="method" label="请求方式" align="center" width="100">
          <template #default="{ row }">
            <el-tag :type="getTagType(row.method)" :class="{ 'el-tag--custom-blue': row.method === 'PUT' }">
              {{ row.method }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="path" label="接口地址" align="center" show-overflow-tooltip />
        <el-table-column prop="permission_info" label="事件名称" align="center" />
        <el-table-column prop="status_code" label="响应码" align="center" width="80">
          <template #default="{ row }">
            <el-tag :type="getCodeType(row.status_code)">
              {{ row.status_code }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="请求耗时" align="center" width="100">
          <template v-slot="scope">{{ scope.row.duration }} ms</template>
        </el-table-column>
        <el-table-column prop="os_info" label="操作系统" align="center" show-overflow-tooltip />
        <el-table-column prop="browser_info" label="浏览器" align="center" show-overflow-tooltip />
      </el-table>
      <!-- 分页 -->
      <Pagination :total="pagination.total" :page="pagination.page" @update:page="updatePage" @update:pageSize="updatePageSize" :page-size="15" />
    </div>
  </div>
</template>

<style scoped>
/* 自定义蓝色标签 */
.el-tag--custom-blue {
  background-color: #EFF0FD;
  color: #626AEF;
  border-color: #ecf5ff;
}
</style>
