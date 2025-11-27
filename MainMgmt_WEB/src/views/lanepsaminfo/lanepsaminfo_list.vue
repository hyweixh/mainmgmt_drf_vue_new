<script setup name="lanepsaminfo_list">
import { ref, reactive, onMounted, watch } from "vue"
import lanepsaminfoHttp from "@/api/lanepsaminfoHttp"; 
import HYMain from "@/components/HYMain.vue";
import HYDialog from "@/components/HYDialog.vue";
import HYPgination from "@/components/HYPgination.vue";
import timeFormatter from "@/utils/timeFormatter"
//import { useAuthStore } from "@/stores/auth";
import { ElMessage } from "element-plus";
import { useRoute, useRouter } from "vue-router"; 
import { showLoading, hideLoading } from '@/utils/loading';
//import '@/assets/css/utilities.css'


const BASE_URL = import.meta.env.VITE_BASE_URL
const route = useRoute();
// 使用 useRouter 钩子来获取 router 实例  
const router = useRouter();
// 定义方法  
 
let dialogVisible = ref(false)
let lanepsaminfos = ref([])
let pagination = reactive({
    page: 1,
    total: 0
})
let page_size = ref() //每页记录数量，和后端一致

 
// 过滤表单,reactive对象类型
let filterForm = reactive({
    stationno: null,
    psamno: null,
    psamstatus_id: null,         
})


// 设备下标
let handleIndex = 0
let psamstatuses = ref([]) // 卡状态
let curr_page = ref()   //当前分页
let tableRef = ref()
let cur_pasamno = ref()
let cur_mem = ref()

function resetFilterForm() {
    filterForm.stationno = null;
    filterForm.psamno = null;
    filterForm.psamstatus_id = null;    
}
// const currentDevice = ref({});

async function requestLanepsaminfos(page, page_size) {
    try {
        let data = await lanepsaminfoHttp.getLanepsaminfoList(page, page_size, filterForm);
        // console.log('API Response:', data);
        let total = data.count;
        pagination.total = total;
        pagination.page = page
        lanepsaminfos.value = data.results;       
    } catch (detail) {
        ElMessage.error(detail);
    }
}

onMounted(async () => {
    requestLanepsaminfos(1, page_size.value)
    try {
        let psamstatuses_data = await lanepsaminfoHttp.getPsamStatus();
        // psamstatuses = await lanepsaminfoHttp.getPsamStatus(); 
        psamstatuses.value = psamstatuses_data;
 
    } catch (error) {       
        ElMessage.error('获取psam卡状态信息失败!');
    }
})

// 监听分页是否有变化  
watch(() => pagination.page, async function (newPage) {
    curr_page.value = newPage;
    requestLanepsaminfos(newPage, page_size.value);
});

// 监听每页多少条记录的变化  
watch(page_size, async function (newSize) {
    // 如果当前不在第一页，重置为第一页  
    if (pagination.page !== 1) {
        pagination.page = 1;
    }
    // 请求新的数据  
    requestLanepsaminfos(1, newSize);
});

const onSearch = (index) => {
    requestLanepsaminfos(1, page_size.value);
}

const onShowDialog = (index) => { 
    cur_pasamno.value = lanepsaminfos.value[index].psamno
    handleIndex = index
    cur_mem.value = lanepsaminfos.value[index].mem    
    dialogVisible.value = true; //显示修改psam卡状态对话框
}
// 修改psam卡状态
const onupdatePsamstatus = async () => {
    await lanepsaminfoHttp.editLanepsam(cur_pasamno.value, cur_mem);
    // console.log("cur_psamno is------ ",cur_pasamno.value)
    ElMessage.success(cur_pasamno.value + "修改成功" )
    dialogVisible.value = false;
    requestLanepsaminfos(curr_page.value, page_size.value);
    }

const onDialogCancel= async () => {        
    dialogVisible.value = false
}    

const onLanepsamInfo_frMSSQL = async () => {  
    showLoading('获取车道PSAM卡信息...')
    try {  
        let data = await lanepsaminfoHttp.get_lanepsaminfo_frMSSQL();        
        // console.log(data);  
        requestLanepsaminfos(1, page_size.value);
        ElMessage.success('获取车道psam卡信息成功！');  
    } catch (error) {  
        console.error('获取psaminfo失败:', error);  
        ElMessage.error('获取数据时发生错误，请稍后重试。'); 
    } finally {
             hideLoading() // ← 必须加
         } 
}
// 导出数据
const export_excels = async () => {
  try {
    // 1. 获取响应对象
    const response = await lanepsaminfoHttp.download_lanepsaminfo();
    
    // 2. 提取 Blob（兼容两种返回方式）
    const blob = response instanceof Blob ? response : response.data;
    
    // 3. 验证 Blob
    if (!blob || !(blob instanceof Blob)) {
      throw new Error(`返回数据不是有效的Blob类型，实际类型: ${typeof blob}`);
    }
    
    // console.log('Blob 大小:', blob.size, '类型:', blob.type); // 调试点

    // 4. 创建下载
    const href = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = href;
    a.download = '车道psam卡.xlsx';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(href);
    
    ElMessage.success('导出成功');
  } catch (error) {
    console.error('导出失败:', error);
    ElMessage.error(error.message || '导出失败');
  }
}; 
 </script>

<template>
    <HYDialog v-model="dialogVisible" title="提示" @submit="onupdatePsamstatus" @cancel="onDialogCancel">
        <div>
            <!-- 移除了 class="dialog-content" 和 flex 布局 -->
            <span style="margin-bottom: 20px; display: block;">您确定修改PSAM卡号：{{ cur_pasamno }}为坏卡吗？</span>
            <el-form-item label="填写坏卡去向">
                <el-input v-model="cur_mem" />
            </el-form-item>
        </div>
    </HYDialog>

    <HYMain title="车道PSAM卡列表" style="margin-top: 10px;">
        <el-card>
            <el-row>
                <el-col :span="8" class="d-flex justify-content-start">
                    <el-button type="primary" icon="plus" @click="onLanepsamInfo_frMSSQL">更新</el-button>
                    <!-- <el-button type="primary" icon="plus" @click="onShowConfirmDialog">确认</el-button> -->
                    <el-button type="primary" icon="download" class="ml-10" @click="export_excels">导出到Excel</el-button>
                </el-col>
                <el-col :span="16" class="d-flex justify-content-end">
                    <el-form-item class="mr-20 font-size-16" label="按站编号" label-width="100px">
                        <el-input  v-number-only v-model="filterForm.stationno" />
                    </el-form-item>
                    <el-form-item class="mr-20 font-size-16" label="按卡号" label-width="100px">                        
                        <el-input 
                            v-model="filterForm.psamno"                              
                            />
                    </el-form-item>
                    <el-form-item class="mr-20 font-size-16" label="按卡状态">
                        <el-select v-model="filterForm.psamstatus_id" placeholder="请选择卡状态" class=select_with>
                            <el-option v-for="p_tatus in psamstatuses" :key="p_tatus.id" :label="p_tatus.psamstatus"
                                :value="p_tatus.id" />
                        </el-select>
                    </el-form-item>
                    <el-button type="primary" icon="Search" @click="onSearch"></el-button>
                    <el-button type="primary" icon="refresh-right" @click="resetFilterForm">重置</el-button>
                </el-col>
            </el-row>
        </el-card>
        <el-card>
            <el-table :data="lanepsaminfos" ref="tableRef" class="lanepsaminfo-table">

                <!-- <el-table-column type="selection" width="55"></el-table-column> -->
                <el-table-column label="序号" width="60">
                    <!-- $index + 1：序号从1开始 -->
                    <template #default="scope">{{ scope.$index + 1 }}</template>
                </el-table-column>
                <el-table-column prop="deviceid" label="设备ID" width="200"></el-table-column>
                <el-table-column prop="stationno" label="站编号" width="80"></el-table-column>
                <el-table-column prop="laneno" label="车道号" width="80"></el-table-column>
                <el-table-column prop="lanecomputerip" label="车道IP" width="150"></el-table-column>
                <el-table-column prop="terminano" label="终端编号" width="150"></el-table-column>
                <el-table-column prop="psamno" label="PSAM卡号" width="200"></el-table-column>
                <el-table-column prop="psamstatus.psamstatus" label="卡状态" width="80">
                    <template #default="scope">
                        <!-- 使用三元运算符来判断卡状态，并据此设置样式 -->
                        <span :style="{ color: scope.row.psamstatus.psamstatus === '坏卡' ? 'red' : '' }">
                            {{ scope.row.psamstatus.psamstatus }}
                        </span>
                    </template>
                </el-table-column>
                <el-table-column prop="first_createtime" label="首次获取时间" width="200">
                    <template #default="scope">
                        {{ timeFormatter.stringFromDateTime(scope.row.first_createtime) }}                    
                    </template>
                </el-table-column>
                <el-table-column prop="last_createtime" label="最后获取时间" width="200">
                    <template #default="scope">
                        <span v-if="scope.row.last_createtime !== null">  
                            {{ timeFormatter.stringFromDateTime(scope.row.last_createtime) }}  
                        </span>                         
                    </template>
                </el-table-column>
                <el-table-column prop="mem" label="备注" class-name="ellipsis-column"></el-table-column>


                <!-- <el-table-column prop="mem" label="备注" class-name="ellipsis-column"></el-table-column> -->
                <el-table-column label="操作">
                    <template #default="scope">
                        <el-button type="primary" icon="Edit" circle @click="onShowDialog(scope.$index)">
                        </el-button>
                    </template>

                </el-table-column>
            </el-table>
            <template #footer>
                <!-- <div style="display: flex; justify-content: space-between;"> -->
                <!-- <el-form-item label="每页：">
                        <el-select v-model="page_size" size="small" style="width: 100px;">
                            <el-option select label="10条/页" :value="1" />
                            <el-option label="20条/页" :value="2" />
                        </el-select>
                    </el-form-item> -->
                <HYPgination v-model="pagination.page" :total="pagination.total"></HYPgination>
                <!-- </div> -->
            </template>
        </el-card>
    </HYMain>
</template>

<style scoped>
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

.lanepsaminfot-table .ellipsis-column .cell {
    white-space: nowrap;
    overflow: hidden;
    /* ellipsis表示文本将被截断，并在末尾显示省略号（...） */
    text-overflow: ellipsis;
}

/* 表格标题加粗 */
.bold-title {
    font-weight: bold;
}

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
        width:200px;  
        margin-right: 20px;
    }

</style>