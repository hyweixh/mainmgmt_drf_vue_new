<script setup name="holidayfree_list">
import { showLoading, hideLoading } from '@/utils/loading'
import { ref, reactive, onMounted, watch } from "vue"
import holidayfreeHttp from "@/api/holidayfreeHttp";
import HYMain from "@/components/HYMain.vue";
import HYPgination from "@/components/HYPgination.vue";
import timeFormatter from '@/utils/timeFormatter';
import { ElMessage } from "element-plus";
import { useRoute, useRouter } from "vue-router"; 

 
const BASE_URL = import.meta.env.VITE_BASE_URL
const route = useRoute();
// 使用 useRouter 钩子来获取 router 实例  
const router = useRouter(); 
// 当前登陆用户
const curLoginUser = ref(JSON.parse(localStorage.getItem('HY_USER_KEY.realname')) || ''); 
let holidayfreeparas = ref([])
let pagination = reactive({
    page: 1,
    total: 0
})
let page_size = ref(15) //每页记录数量，和后端一致
 
// 使用 ref 来创建响应式数据  
const value1 = ref([
    // new Date(2023, 9, 1, 12, 0, 0), // 假设默认开始时间是2023年10月1日12:00:00  
    // new Date(2023, 9, 2, 12, 0, 0)  // 假设默认结束时间是2023年10月2日12:00:00 
]); // 使用数组来绑定日期时间范围  
const pickerOptions = ref({}); // 默认情况下，pickerOptions 是空的  
  
  
// 过滤表单,reactive对象类型
let filterForm = reactive({
    inspectresult: null, 
    starttime: null,       
})

let curr_page = ref()   //当前分页
let tableRef = ref()

// 取10天以前的日期
const now = new Date();  
const tenDaysAgo = new Date(now);  
tenDaysAgo.setDate(tenDaysAgo.getDate() - 10);  

function resetFilterForm() {
    filterForm.inspectresult = null; 
    filterForm.starttime='';   
}

const onSearch = (index) => {
    requestHolidayPara(1, page_size.value) ;
}

const onholidayfree_update = async () => {  
    showLoading('正在获取车道免费参数...')
    try {  
        let data = await holidayfreeHttp.get_holidayfree_frlane();      
        requestHolidayPara(1, page_size.value);  
        ElMessage.success('获取车道免费参数成功！');  
    } catch (error) {         
        ElMessage.error('获取数据时发生错误，请稍后重试。'); 
    }  
    finally {
             hideLoading() // ← 必须加
         }
}
async function requestHolidayPara(page, page_size) {
    // showLoading('正在查询节假日免费参数...')
    try {
        let data = await holidayfreeHttp.getholidayfreeList(page, page_size, filterForm);
        // console.log('API Response:', data);
        let total = data.count;
        pagination.total = total;
        pagination.page = page
        holidayfreeparas.value = data.results;       
    } catch (detail) {
        ElMessage.error(detail);
    }
}

onMounted(async () => {
    requestHolidayPara(1, page_size.value);   
})

// 监听分页是否有变化  
watch(() => pagination.page, async function (newPage) {  
    curr_page.value = newPage;  // 使用 .value 来更新 ref 的值  
    requestHolidayPara(curr_page.value, page_size.value);  // 使用 curr_page.value 而不是硬编码的 1  
});

// 监听每页多少条记录的变化  
watch(page_size, async function (newSize) {
    // 如果当前不在第一页，重置为第一页  
    if (pagination.page !== 1) {
        pagination.page = 1;
    }
    // 请求新的数据  
    requestHolidayPara(1, page_size.value) ;
});

// 定义一个函数来比较日期 
function isStartTimeBeforeTenDaysAgo(startTime) {  
    // 获取当前时间并计算10天前的日期  
    // const now = new Date();  
    // const tenDaysAgo = new Date(now);  
    // tenDaysAgo.setDate(tenDaysAgo.getDate() - 10);  
  
    // 比较两个 Date 对象    
    // console.log("当前时间：", now);  
    // console.log("10天前：", tenDaysAgo);  
  
    // 检查 startTime 是否在当前时间10天之前  
    return startTime < tenDaysAgo;  
}  
</script>

<template>
    <HYMain title="节假日免费参数" style="margin-top: 10px;">
        <el-card class="custom-card">
        <el-row type="flex" align="middle">
            <el-col :span="6" class="d-flex justify-content-start align-items-center" >
                <el-button type="primary" icon="plus" @click="onholidayfree_update">更新</el-button>
                <!-- <el-button type="primary" icon="plus" @click="onShowConfirmDialog">确认</el-button> -->
            </el-col>
            <el-col :span="18" class="d-flex justify-content-end align-items-center" >
                <el-form-item label="按检查结果" label-width="100px" class="mr-20 font-size-16" 
                    style="white-space: nowrap; flex-shrink: 0;">    
                    <el-select v-model="filterForm.inspectresult" placeholder="请选择检查结果" class="select_with">
                        <el-option label="获取成功" value="获取成功"></el-option>
                        <el-option label="获取失败" value="获取失败"></el-option>
                    </el-select>
                </el-form-item>
                <el-form-item label="按开始日期" label-width="100px"  class="mr-20 font-size-14">
                    <el-input v-model="filterForm.starttime" placeholder="开始日期时间(2024-10-01)" class="select_with"></el-input>
                </el-form-item>
            <el-button type="primary" icon="Search" @click="onSearch"></el-button>
            <el-button type="primary" icon="refresh-right" @click="resetFilterForm">重置</el-button>
            </el-col>
        </el-row>
        </el-card>
        <el-card>
            <el-table :data="holidayfreeparas" ref="tableRef" class="gantrypsaminfo-table">

                <!-- <el-table-column type="selection" width="55"></el-table-column> -->
                <el-table-column label="序号" width="60">
                    <!-- $index + 1：序号从1开始 -->
                    <template #default="scope">{{ scope.$index + 1 }}</template>
                </el-table-column>
                <!-- <el-table-column prop="tollid" label="收费单元编号" width="200"></el-table-column> -->
                <el-table-column prop="stationno" label="站编码" width="100"></el-table-column>
                <el-table-column prop="laneno" label="车道编码" width="100"></el-table-column>
                <el-table-column prop="lanecomputerip" label="车道IP" width="130"></el-table-column>
                <el-table-column prop="lanetype" label="车道类型" width="120"></el-table-column>

                <el-table-column prop="verid" label="版本号" width="100">
                    <template #default="scope">
                        <span :style="{ color: scope.row.verid === '000' ? 'red' : '' }">
                            {{ scope.row.verid }}
                        </span>
                    </template>
                </el-table-column>
                <el-table-column prop="starttime" label="开始时间" width="180">
                    <template #default="scope">
                        <span :style="{
                            color: scope.row.verid === '000' ? 'red' :
                                isStartTimeBeforeTenDaysAgo(new Date(scope.row.starttime)) ? '#6699CC' : 'black'
                        }">
                            {{ timeFormatter.stringFromDateTime(scope.row.starttime) }}
                        </span>
                    </template>
                </el-table-column>
                
                <el-table-column prop="overtime" label="结束时间" width="180">
                    <template #default="scope">
                        <span :style="{
                            color: scope.row.verid === '000' ? 'red' :
                                isStartTimeBeforeTenDaysAgo(new Date(scope.row.starttime)) ? '#6699CC' : 'black'
                        }">
                            {{ timeFormatter.stringFromDateTime(scope.row.overtime) }}
                        </span>
                    </template>
                </el-table-column>
                <el-table-column prop="inspector" label="检查人员" width="100"></el-table-column>
                <el-table-column prop="inspecttime" label="检查时间" width="180">
                    <template #default="scope">
                        {{ timeFormatter.stringFromDateTime(scope.row.inspecttime) }}
                    </template>
                </el-table-column>
                <el-table-column prop="inspectresult" label="检查结果" width="100">
                    <template #default="scope">
                        <span :style="{
                            color: scope.row.inspectresult === '获取失败' ? 'red' :
                                isStartTimeBeforeTenDaysAgo(new Date(scope.row.starttime)) ? '#6699CC' :
                                    'black'
                        }">
                            {{ scope.row.inspectresult }}
                        </span>
                    </template>
                </el-table-column>
                <el-table-column prop="confirmer" label="确认人员" width="110"></el-table-column>
                <el-table-column prop="confirmdatetime" label="确认时间" width="180"></el-table-column>
                <el-table-column prop="isconfirm" label="是否确认" width="180"></el-table-column>
            </el-table>
            <template #footer>
                <HYPgination v-model="pagination.page" :total="pagination.total"></HYPgination>
            </template>
        </el-card>
    </HYMain>
</template>

<style scoped>
    .select_with {
        width: 180px;  /* 两个控件宽度一致 */
    }
    /* 卡片内边距样式 */
    .custom-card :deep(.el-card__body) {
    padding-top: 15px;
    padding-bottom: 15px;
    }
    /* 下拉框表单宽度 */
    .my-form-inline .el-select {
        --el-select-width: 150px;
    }

    .my-form-inline .el-input {
        --el-input-width: 200px;
    }

    .el-badge {
        margin-right: 2px;
        margin-top: 2px;
    }

    .el-tag {
        margin-right: 2px;
    }

    /* 表格标题加粗 */
    .bold-title {
        font-weight: bold;
    }


    /* .d-flex { display: flex; }
    .justify-content-start { justify-content: flex-start; }
    .justify-content-end { justify-content: flex-end; }
    .align-items-center { align-items: center; }  /* 新增这一行 */
    /*.select_with { width: 200px; margin-right: 20px; } */
</style>