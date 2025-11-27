<script setup name="gantrypsaminfo_list">
import { ref, reactive, onMounted, watch } from "vue"
import gantrypsaminfoHttp from "@/api/gantrypsaminfoHttp";
import HYMain from "@/components/HYMain.vue";
import HYDialog from "@/components/HYDialog.vue";
import HYPgination from "@/components/HYPgination.vue";
import timeFormatter from '@/utils/timeFormatter';
import { ElMessage } from "element-plus";
import { useRoute, useRouter } from "vue-router";

const BASE_URL = import.meta.env.VITE_BASE_URL
const route = useRoute();
// 使用 useRouter 钩子来获取 router 实例  
const router = useRouter();
// 定义方法  

let dialogVisible = ref(false)
let gantrypsaminfos = ref([])
let pagination = reactive({
    page: 1,
    total: 0
})
let page_size = ref() //每页记录数量，和后端一致


// 过滤表单,reactive对象类型
let filterForm = reactive({
    pilenumber: null,
    psamno: null,
    statusName: null,
})


// 设备下标
let handleIndex = 0
let psamstatuses = ref([]) // 卡状态
let curr_page = ref()   //当前分页
let tableRef = ref()
let cur_pasamno = ref()
let cur_mem = ref()

function resetFilterForm() {
    filterForm.pilenumber = null;
    filterForm.psamno = null;
    filterForm.statusName = null;
}

async function requestgantrypsaminfos(page, page_size) {
    try {
        let data = await gantrypsaminfoHttp.getGantrypsaminfoList(page, page_size, filterForm);
        // console.log('API Response:', data);
        let total = data.count;
        pagination.total = total;
        pagination.page = page
        gantrypsaminfos.value = data.results;
    } catch (detail) {
        ElMessage.error(detail);
    }
}

onMounted(async () => {
    requestgantrypsaminfos(1, page_size.value)

})

// 监听分页是否有变化  
watch(() => pagination.page, async function (newPage) {
    curr_page.value = newPage;
    requestgantrypsaminfos(newPage, page_size.value);
});

// 监听每页多少条记录的变化  
watch(page_size, async function (newSize) {
    // 如果当前不在第一页，重置为第一页  
    if (pagination.page !== 1) {
        pagination.page = 1;
    }
    // 请求新的数据  
    requestgantrypsaminfos(1, newSize);
});

const onSearch = (index) => {
    requestgantrypsaminfos(1, page_size.value);
}

const onShowDialog = (index) => {
    cur_pasamno.value = gantrypsaminfos.value[index].psamno
    handleIndex = index
    cur_mem.value = gantrypsaminfos.value[index].mem    
    
    // cur_mem = gantrypsaminfos.value[index].mem    
    dialogVisible.value = true; //显示修改psam卡状态对话框
}
// 修改psam卡状态
const onupdatePsamstatus = async () => {
    // console.log("cur_psamno is ",cur_pasamno.value)
    let data = await gantrypsaminfoHttp.editgantrypsam(cur_pasamno.value, cur_mem);
    // 
    ElMessage.success(cur_pasamno.value + "修改成功")
    dialogVisible.value = false;
    // router.push({ name: 'gantrypsaminfo_list', });
    requestgantrypsaminfos(curr_page, page_size.value);
}

const ongantrypsaminfo_frMSSQL = async () => {
    try {
        let data = await gantrypsaminfoHttp.get_gantrypsaminfo_frMSSQL();
        // console.log(data);  
        requestgantrypsaminfos(1, page_size.value);
        ElMessage.success('获取门架psam卡信息成功！');
    } catch (error) {
        console.error('获取psaminfo失败:', error);
        ElMessage.error('获取数据时发生错误，请稍后重试。');
    }
}

const onDialogCancel = async () => {
    dialogVisible.value = false
}

const export_excels = async () =>{  
      try {    
        const response = await gantrypsaminfoHttp.downloadGantrypsaminfo();  
        let href = URL.createObjectURL(response.data)  
        // console.log("response.data====",response.data)
        const a = document.createElement("a")
        a.href = href        
        a.setAttribute('download', '门架psam卡.xlsx')       
        document.body.appendChild(a)       
        a.click()
      
        document.body.removeChild(a)       
        URL.revokeObjectURL(href)    
      } catch (error) {    
        console.error('Error exporting Excel:', error);    
      }    
    } 
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

    <HYMain title="门架PSAM卡列表" style="margin-top: 10px;">
        <el-card>
            <el-row>
                <el-col :span="8" class="d-flex justify-content-start">
                    <el-button type="primary" icon="plus" @click="ongantrypsaminfo_frMSSQL">更新</el-button>
                    <el-button type="primary" icon="download" class="ml-10" @click="export_excels">导出到Excel</el-button>
                </el-col>
                <el-col :span="16" class="d-flex justify-content-end">
                    <el-form-item class="mr-20 font-size-16" label="按桩号" label-width="100px">
                        <el-input v-model="filterForm.pilenumber" />
                    </el-form-item>
                    <el-form-item class="mr-20 font-size-16" label="按卡号" label-width="100px">
                        <el-input v-model="filterForm.psamno" />
                    </el-form-item>
                    <el-form-item class="mr-20 font-size-16" label="按卡状态">
                        <el-select v-model="filterForm.statusName" placeholder="请选择卡状态" class=select_with>
                            <el-option label="正常" value="正常"></el-option>
                            <el-option label="未授权" value="未授权"></el-option>
                            <el-option label="异常" value="异常"></el-option>
                            <el-option label="坏卡" value="坏卡"></el-option>
                        </el-select>
                    </el-form-item>
                    <el-button type="primary" icon="Search" @click="onSearch"></el-button>
                    <el-button type="primary" icon="refresh-right" @click="resetFilterForm">重置</el-button>
                </el-col>
            </el-row>
        </el-card>

        <el-card>
            <el-table :data="gantrypsaminfos" ref="tableRef" class="gantrypsaminfo-table">
                <!-- <el-table-column type="selection" width="55"></el-table-column> -->
                <el-table-column label="序号" width="60">
                    <!-- $index + 1：序号从1开始 -->
                    <template #default="scope">{{ scope.$index + 1 }}</template>
                </el-table-column>
                <el-table-column prop="tollid" label="收费单元编号" width="200"></el-table-column>
                <el-table-column prop="position" label="门架区间" width="200"></el-table-column>
                <el-table-column prop="pilenumber" label="桩号" width="100"></el-table-column>
                <el-table-column prop="rsuid" label="RSUID" width="100"></el-table-column>
                <el-table-column prop="controlid" label="控制器ID" width="120"></el-table-column>
                <el-table-column prop="channelid" label="通道号" width="120"></el-table-column>
                <el-table-column prop="psamno" label="PSAM卡号" width="200"></el-table-column>
                <el-table-column prop="statusName" label="PSAM状态" width="100">
                    <template #default="scope">
                        <!-- 使用三元运算符来判断卡状态，并据此设置样式 -->
                        <span :style="{ color: scope.row.statusName === '坏卡' ? 'red' : '' }">
                            {{ scope.row.statusName }}
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
                        <!-- {{ timeFormatter.stringFromDateTime(scope.row.last_createtime) }}     -->  
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
                <HYPgination v-model="pagination.page" :total="pagination.total"></HYPgination>
            </template>
        </el-card>
    </HYMain>
</template>

<style scoped>
/* 下拉框表单宽度 */
/* .my-form-inline .el-select {
    --el-select-width: 150px;
}

.my-form-inline .el-input {
    --el-input-width: 200px;
} */

.el-badge {
    margin-right: 2px;
    margin-top: 2px;
}

.el-tag {
    margin-right: 2px;
}

.gantrypsaminfot-table .ellipsis-column .cell {
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