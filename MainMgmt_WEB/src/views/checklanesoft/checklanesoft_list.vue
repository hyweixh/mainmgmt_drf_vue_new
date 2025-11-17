<script setup name="checklanesoft_list">
import { ref, reactive, onMounted, watch } from "vue"
import checklanesoftHttp from "@/api/checklanesoftHttp"
import HYMain from "@/components/HYMain.vue";
import HYDialog from "@/components/HYDialog.vue";
import HYPgination from "@/components/HYPgination.vue";
import timeFormatter from '@/utils/timeFormatter';
import { ElMessage } from "element-plus";
import { useRoute, useRouter } from "vue-router";
import { showLoading, hideLoading } from '@/utils/loading'


const BASE_URL = import.meta.env.VITE_BASE_URL
const route = useRoute();
// 使用 useRouter 钩子来获取 router 实例  
const router = useRouter();
let dialogVisible = ref(false)
let ConfirmdialogVisible = ref(false)
let downloadDialogVisible = ref(false)
let is_history = ref(false)
let selectMonth =ref([])

let lanesoftparas = ref([])
let pagination = reactive({
    page: 1,
    total: 0
})
let page_size = ref(10) //每页记录数量，和后端一致  
// 过滤表单,reactive对象类型
let filterForm = reactive({
    queryType: '',
    queryCondition:[],
})
let queryConditions = ref([])
 
let curr_page = ref()   //当前分页
let tableRef = ref()

const onLaneSoftPSara_frMSSQL = async () => {  
    showLoading('正在查询，请等待...')
    try {  
        is_history.value=false
        let data = await checklanesoftHttp.get_lanesoftparams_frMSSQL();        
        requestLanesoftparas(0,1, page_size.value);
        ElMessage.success('获取车道软件参数成功！');  
    } catch (error) {  
        console.error('获获取车道软件参数失败:', error);  
        ElMessage.error('获取数据时发生错误，请稍后重试。'); 
    }  finally {
        hideLoading() // ✅ 正确关闭方式
    }
}

async function requestLanesoftparas(firm,page, page_size) {    
    try {
        let data = await checklanesoftHttp.getlanesoftparasList(firm,page, page_size, filterForm);
        let lanesoftParasArray = data.results; // 获取结果数组  
        // console.log("data:", lanesoftParasArray); 
        // 将 ISO 8601 字符串转换为日期对象，并找到最大的日期  
        // lane 是 lanesoftParasArray.reduce 方法回调函数的第二个参数，代表数组中当前正在处理的元素,即（data.results）
        const maxInspectTime = lanesoftParasArray.reduce((max, lane) => {  
            const currentTime = new Date(lane.inspecttime); // 假设每个lane对象都有一个inspecttime字段  
            return (max && max > currentTime) ? max : currentTime; // 注意这里的比较，确保max是有效的Date对象  
        }, '2020-01-01'); // 初始值设为null，因为我们会在第一次迭代中设置它  
  
        // 检查maxInspectTime是否为null（在没有inspecttime字段或数组为空的情况下会发生）  
        if (maxInspectTime === null) {  
            console.error("No inspecttime found or results array is empty");  
            // 可以选择在这里抛出一个错误或返回一个错误消息  
        } else {  
            console.log("max date:", timeFormatter.stringFromDateTime(maxInspectTime).split(" ")[0]);  
        }           
        let total = data.count;
        pagination.total = total;
        pagination.page = page
        lanesoftparas.value = data.results;
        return { records: data.results, total: total ,maxInspectTime:maxInspectTime};
    } catch (detail) {
        ElMessage.error(`Error fetching data: ${detail.message}`);

    }
}

const onSearch = (index) => {
    requestLanesoftparas(0, 1, page_size.value);
 }

 const onShowConfirmDialog = async (index) => {  
    try {  
        // const confifrmData = await checklanesoftHttp.getlanesoftparasList(1,1, page_size, filterForm);
        // const data = await checklanesoftHttp.getlanesoftparasList(0,1, page_size, filterForm);
        const confifrmData = await requestLanesoftparas(1,1, page_size);  // 获取已确认的数据
        const data = await requestLanesoftparas(0,1, page_size);  // 获取未确认的数据
        if (data.length === 0){
            maxDate_str='2020-01-01' 
        }
        if (confifrmData.length === 0){
            confirmMaxDate_str='2020-01-01' 
        }
       // 定义一个函数来安全地获取格式化后的日期字符串  
       const getFormattedDate = (dateTime) => {  
            // 假设 timeFormatter.stringFromDateTime 能够处理无效输入并返回字符串  
            // 但为了安全起见，我们在这里进行额外的检查  
            const dateString = (dateTime && typeof dateTime === 'string' && dateTime.length > 0)  
                ? dateTime.split(" ")[0]  
                : '2020-01-01'; // 默认值  
            return dateString;  
        };  
        // console.log("data.maxInspectTime",data.maxInspectTime,"confifrmData.maxInspectTime",confifrmData.maxInspectTime)  
        let maxDate_str = timeFormatter.stringFromDateTime(data.maxInspectTime); 
        let confirmMaxDate_str = timeFormatter.stringFromDateTime(confifrmData.maxInspectTime); 
        let maxDate = getFormattedDate(maxDate_str);  
        let confirmMaxDate = getFormattedDate(confirmMaxDate_str); 
        console.log("maxDate:",maxDate,"confirmMaxDate:",confirmMaxDate)
        if (maxDate !== '2020-01-01' && maxDate === confirmMaxDate && confirmMaxDate !== '2020-01-01'){
            ElMessage.info(maxDate+'数据已确认！')
        } else if (data.total > 0)  {      
            ConfirmdialogVisible.value = true;    
        }  
        else {    
            ElMessage.info('没有未确认的数据');    
        }  
  
    } catch (error) {  
        // console.error('请求数据时出错:', error);  
        ElMessage.error('请求数据时出错，请稍后再试');  
    }  
}

const onCheckSoftwareLaneConfirm = async () => {    
    try{        
        is_history.value=true;
        let data = await checklanesoftHttp.confirm_checklanesoft();
        ConfirmdialogVisible.value = false
        requestLanesoftparas(1, 1, page_size.value);
        // router.push({ name: 'checklanesoft_list'});
        ElMessage.success("确认成功！")   
            
    }
    catch (detail) {
        ElMessage.error(`Error fetching data: ${detail.message}`);
    }
}   
// 处理HYDialog取消按钮点击后的逻辑
const onDialogCancel= async () => {    
    dialogVisible.value = false    
    ConfirmdialogVisible.value = false
    downloadDialogVisible.value = false
    
    }  
   
onMounted(async () => {
    await requestLanesoftparas(0, 1, page_size.value);
})

// 监听分页是否有变化  
watch(() => pagination.page, async function (newPage) {
    curr_page.value = newPage;
    requestLanesoftparas(0, curr_page, page_size.value);
});

// 监听每页多少条记录的变化  
watch(page_size, async function (newSize) {
    // 如果当前不在第一页，重置为第一页  
    if (pagination.page !== 1) {
        pagination.page = 1;
    }
    // 请求新的数据  
    requestLanesoftparas(0, 1, page_size.value);
});

// 定义方法  
const handleQueryTypeChange = async (newQueryType) => {  
    try {  
        let response = await checklanesoftHttp.get_queryCondition(newQueryType);  
        filterForm.queryCondition = response.data
        queryConditions.value = filterForm.queryCondition
    } catch (error) {  
        console.error("Error fetching data:", error);  
    }  
}; 
// 监视 filterForm.queryType 的变化  
watch(() => filterForm.queryType, (newValue, oldValue) => {       
    handleQueryTypeChange(newValue);  
});  

// let data = reactive({
//     value1: '',
//     value2: ''
// })
// 更新故障原因和处理方法
const onupdateerror_des_proc = async () => {
    // let cur_id = ref(),cur_id，定义为响应式变量，传递参数时需用.value
    let data = await checklanesoftHttp.update_error_desc_proc(
        cur_id.value, 
        cur_error_des.value,
        cur_error_proc.value);
    
    ElMessage.success("修改故障描述/处理成功！" )
    dialogVisible.value = false;
    // router.push({ name: 'lanepsaminfo_list', });
    requestLanesoftparas(0,curr_page, page_size.value);
    }

let cur_id = ref()
let cur_stationname = ref()
let cur_laneno = ref()
let cur_error_des = ref()
let cur_error_proc = ref()
const onErrorinfo = (index) => { 
    cur_id.value =  lanesoftparas.value[index].id
    cur_stationname.value = lanesoftparas.value[index].tollStationname
    cur_laneno.value = lanesoftparas.value[index].laneno
    dialogVisible.value = true; //显示填写错误信息对话框
}
// 显示历史记录
const onLaneSoftPara_history = async () => {
    // is_history=true
    requestLanesoftparas(1,curr_page, page_size.value);
}

const export_excels = async () =>{    
   //  ElMessage.success(selectMonth.value)
    downloadDialogVisible.value = true      
    }    

const onDownload =async () =>{
    // ElMessage.success(timeFormatter.stringFromDate(selectMonth.value))
    let selectY = timeFormatter.stringFromDate(selectMonth.value).split('-')[0]
    let selectM = timeFormatter.stringFromDate(selectMonth.value).split('-')[1]
    let selectYM =  selectY+'-'+ selectM
    // console.log("导出日期：",selectYM)
    try {    
        const response = await checklanesoftHttp.download_checklanesoft(selectYM);  
        let href = URL.createObjectURL(response.data)  
        // console.log("response.data====",response.data)
        const a = document.createElement("a")
        a.href = href        
        a.setAttribute('download', '车道软件参数.xlsx')       
        document.body.appendChild(a)       
        a.click()
      
        document.body.removeChild(a)       
        URL.revokeObjectURL(href)    
      } catch (error) {    
        ElMessage.error('导出Excel表错误！', error);          
      }    
    }
// const onDownload = async () => {  
//     let selectY = timeFormatter.stringFromDate(selectMonth.value).split('-')[0];  
//     let selectM = timeFormatter.stringFromDate(selectMonth.value).split('-')[1];  
//     let selectYM = selectY + '-' + selectM;  
  
//     try {  
//         const response = await checklanesoftHttp.download_checklanesoft(selectYM);  
//         if (!response || !response.data) {  
//             throw new Error('服务器返回空响应或没有数据');  
//         }  
//         let href = URL.createObjectURL(new Blob([response.data]));  // 确保response.data是Blob或ArrayBuffer  
//         const a = document.createElement("a");  
//         a.href = href;  
//         a.setAttribute('download', '车道软件参数.xlsx');  
//         document.body.appendChild(a);  
//         a.click();  
//         document.body.removeChild(a);  
//         URL.revokeObjectURL(href);  
//     } catch (error) {  
//         // 打印错误详细信息到控制台（开发时使用）  
//         ElMessage.error('导出Excel表错误！', error);  
          
//         // 检查错误对象是否有响应属性  
//         if (error.response) {  
//             // 例如，Axios 的错误对象有 status 和 statusText 属性  
//             ElMessage.error('Status:', error.response.status);  
//             ElMessage.error('Status Text:', error.response.statusText);  
//             // 如果需要，还可以打印出响应数据  
//             ElMessage.error('Response Data:', error.response.data);  
//         } else {  
//             // 处理没有响应的错误（例如网络问题）  
//             ElMessage.error('请求失败，没有响应');  
//         }  
          
//         // 显示用户友好的错误消息  
//         ElMessage.error('导出Excel表错误！', '具体错误信息：' + (error.message || '未知错误'));  
//     }  
// }
</script>
<template>
    <HYDialog v-model="ConfirmdialogVisible" title="提示" @submit="onCheckSoftwareLaneConfirm" @cancel="onDialogCancel">
        <div>
            <span style="margin-bottom: 20px; display: block;">请完成检查后，再确认！</span>
        </div>
    </HYDialog>
    <HYDialog v-model="dialogVisible" title="异常处理" @submit="onupdateerror_des_proc" @cancel="onDialogCancel">
        <div>
            <!-- 移除了 class="dialog-content" 和 flex 布局 -->
            <span style="margin-bottom: 20px; display: block;">当前车道：{{ cur_stationname }}-{{cur_laneno}}</span>
            <el-form-item label="错误描述">
                <el-input v-model="cur_error_des" />
            </el-form-item>
            <el-form-item label="异常处理">
                <el-input v-model="cur_error_proc" />
            </el-form-item>
        </div>
    </HYDialog>
    <HYDialog v-model="downloadDialogVisible" title="请选择月份" @submit="onDownload" @cancel="onDialogCancel">
        <div class="container">
            <div class="block">
                <span class="demonstration" style="margin-left: 40px;">月</span>
                <el-date-picker style="margin-left: 20px;" v-model="selectMonth" type="month" placeholder="选择月"
                    @change="handleMonthChange">
                </el-date-picker>
            </div>
        </div>
    </HYDialog>

    <HYMain title="车道软件参数" style="margin-top: 10px;">
        <el-card>
            <el-row>
                <el-col :span="8" class="d-flex justify-content-start">
                    <el-button type="primary" icon="plus" @click="onLaneSoftPSara_frMSSQL">更新</el-button>
                    <el-button type="primary" icon="plus" @click="onShowConfirmDialog">确认</el-button>
                    <el-button type="primary" icon="plus" @click="onLaneSoftPara_history">历史记录</el-button>
                    <el-button type="primary" icon="download" class="ml-10" @click="export_excels">导出到Excel</el-button>
                </el-col>
                <el-col :span="16" class="d-flex justify-content-end">
                    <el-form-item label="查询类型" label-width="80px">
                        <el-select v-model="filterForm.queryType" placeholder="请选择查询类型" class=select_with>
                            <el-option label="OBU黑名单" value="obublacklistversion"></el-option>
                            <el-option label="最小费率" value="spcrateversion"></el-option>
                            <el-option label="承载门架费率" value="lanerateversion"></el-option>
                            <el-option label="车道软件版本" value="opsver"></el-option>
                        </el-select>
                    </el-form-item>

                    <el-form-item label="查询条件" label-width="80px">
                        <el-select v-model="filterForm.queryCondition" placeholder="请选择条件" class=select_with>
                            <el-option v-for="condition in queryConditions" :key="condition" :label="condition"
                                :value="condition">
                            </el-option>
                        </el-select>
                    </el-form-item>

                    <el-button type="primary" icon="el-icon-refresh-right" class="mt-10"
                        @click="onSearch">执行</el-button>
                </el-col>
            </el-row>
        </el-card>
        <el-card>
            <el-table :data="lanesoftparas" ref="tableRef">
                <!-- <el-table-column label="序号" width="60"> -->
                <!-- $index + 1：序号从1开始 -->
                <!-- <template #default="scope">{{ scope.$index + 1 }}</template>
                </el-table-column> -->
                <!-- <el-table-column prop="stationno" label="站编码" width="80"></el-table-column>                -->
                <el-table-column prop="tollStationname" label="站名" width="120"></el-table-column>
                <el-table-column prop="laneno" label="车道编码" width="80"></el-table-column>
                <el-table-column prop="lanetypename" label="车道类型" width="100"></el-table-column>

                <el-table-column prop="obublacklistversion" label="OBU状态名单" width="200"></el-table-column>
                <el-table-column prop="spcrateversion" label="最小费率版本" width="120"></el-table-column>
                <el-table-column prop="greenreservelistversion" label="绿通预约" width="125"></el-table-column>
                <!-- <el-table-column prop="bulkvehreserveversion" label="大件运输车" width="125"></el-table-column> -->
                <!-- <el-table-column prop="laneservtime" label="车道时间" width="180"></el-table-column> -->
                <el-table-column prop="laneservtime" label="车道时间" width="180">
                    <template #default="scope">
                        <span :style="{ color: scope.row.laneservtime !== scope.row.lanebeidoutime ? 'red' : 'black' }">
                            {{ scope.row.laneservtime }}
                        </span>
                    </template>
                </el-table-column>
                <el-table-column prop="lanebeidoutime" label="北斗时间" width="180">
                    <template #default="scope">
                        <span :style="{ color: scope.row.laneservtime !== scope.row.lanebeidoutime ? 'red' : 'black' }">
                            {{ scope.row.lanebeidoutime }}
                        </span>
                    </template>
                </el-table-column>

                <el-table-column prop="lanerateversion" label="承载门架费率" width="225"></el-table-column>
                <el-table-column prop="opsver" label="车道软件版本" width="200"></el-table-column>
                <!-- <el-table-column prop="inspector" label="检查人员" width="100"></el-table-column> -->
                <!-- <el-table-column prop="inspecttime" label="检查时间" width="180"></el-table-column> -->
                <!-- <el-table-column prop="inspectresult" label="检查结果" width="180"></el-table-column> -->

                <!-- <el-table-column prop="inspector" label="确认人员" width="100"></el-table-column> -->
                <!-- <el-table-column prop="inspecttime" label="确认时间" width="180"></el-table-column> -->

                <el-table-column prop="isconfirm" label="是否确认" width="80"></el-table-column>
                <el-table-column prop="error_desc" label="错误描述" width="120"></el-table-column>
                <el-table-column prop="error_proc" label="错误处理" width="120"></el-table-column>
                <el-table-column label="操作" v-if="!is_history">
                    <template #default="scope">
                        <el-button type="primary" icon="-edit" circle @click="onErrorinfo(scope.$index)">
                        </el-button>
                    </template>
                </el-table-column>

            </el-table>
            <template #footer>
                <div>
                    <HYPgination v-model="pagination.page" :total="pagination.total"></HYPgination>
                </div>
            </template>
        </el-card>
    </HYMain>
</template>

<style scoped>  
    .d-flex {  
        display: flex;  
    }  
    .justify-content-start {  
        justify-content: flex-start;  
    }  
    .justify-content-end {  
        justify-content: flex-end;  
    }  
    .align-items-flex-end {  
        align-items: flex-end;  
    }  
    .flex-column {  
        flex-direction: column;  
    }  
    .select_with{
        width:300px;  
        margin-right: 20px;
    }
</style>