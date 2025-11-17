<script setep name="checklanesoft_list">
import { ref, reactive, onMounted, watch } from "vue"
import checklanesoftHttp from "@/api/checklanesoftHttp"; 
import HYMain from "@/components/HYMain.vue";
import HYDialog from "@/components/HYDialog.vue";
import HYPgination from "@/components/HYPgination.vue";
import { useAuthStore } from "@/stores/auth";
import { ElMessage } from "element-plus";
import { useRoute, useRouter } from "vue-router"; 
 
const BASE_URL = import.meta.env.VITE_BASE_URL
const route = useRoute();
// 使用 useRouter 钩子来获取 router 实例  
const router = useRouter(); 


let lanesoftparas = ref([])
let pagination = reactive({
    page: 1,
    total: 0
})
let page_size = ref(10) //每页记录数量，和后端一致
let filterForm = reactive({
    pilenumber: null,
    psamno: null,
    statusName: null,         
})

async function requestLanesoftparas(page, page_size) {
    try {
        let data = await checklanesoftHttp.getlanesoftparasList(page, page_size, filterForm);
        console.log('API Response========:', data);
        let total = data.count;
        pagination.total = total;
        pagination.page = page
        lanesoftparas.value = data.results;       
    } catch (detail) {
        ElMessage.error(detail);
    }
}

onMounted(async () => {
  requestLanesoftparas(1, page_size.value);     
})

</script>
<template>
   <HYMain title="车道软件参数" style="margin-top: 10px;">
        <el-form-item>
                    <el-button type="primary" icon="Plus" @click="onholidayfree_update">更新车道软件参数</el-button>
                    <el-button type="primary" icon="Download" @click="export_excels">导出到EXELS</el-button>
                </el-form-item>
        <el-card>
            <el-table :data="lanesoftparas" ref="tableRef"  > 
                <el-table-column label="序号" width="60">
                    <!-- $index + 1：序号从1开始 -->
                    <template #default="scope">{{ scope.$index + 1 }}</template>
                </el-table-column>
                <el-table-column prop="stationno" label="站编码" width="200"></el-table-column>               
                <el-table-column prop="tollStationname" label="站名" width="70"></el-table-column>
                <el-table-column prop="laneno" label="车道编码" width="80"></el-table-column>
                <el-table-column prop="lanetypename" label="车道类型" width="130"></el-table-column>
                <el-table-column prop="lanetype" label="车道类型" width="120"></el-table-column>
            
                <el-table-column prop="obublacklistversion" label="OBU黑名单版本" width="100"></el-table-column>
                <el-table-column prop="spcrateversion" label="最小费率版本" width="100"></el-table-column>
                <el-table-column prop="greenreservelistversion" label="绿通车辆白名单" width="100"></el-table-column>
                <el-table-column prop="bulkvehreserveversion" label="大件运输车版本号" width="100"></el-table-column>
                <el-table-column prop="laneservtime" label="车道时间" width="100"></el-table-column>
                <el-table-column prop="lanebeidoutime" label="北斗时间" width="100"></el-table-column>
                <el-table-column prop="lanerateversion" label="最小费率版本" width="100"></el-table-column>
                <el-table-column prop="opsver" label="车道软件版本" width="100"></el-table-column>   
                <el-table-column prop="inspector" label="检查人员" width="100"></el-table-column>
                <el-table-column prop="inspecttime" label="检查时间" width="180"></el-table-column>
                <el-table-column prop="inspectresult" label="检查结果" width="180"></el-table-column>
                
                <el-table-column prop="inspector" label="确认人员" width="100"></el-table-column>
                <el-table-column prop="inspecttime" label="确认时间" width="180"></el-table-column>
                
                <el-table-column prop="isconfirm" label="是否确认" width="180"></el-table-column>
                <el-table-column prop="error_desc" label="错误描述" width="180"></el-table-column>
                <el-table-column prop="error_proc" label="错误处理" width="180"></el-table-column>
                 
            </el-table>
            <template #footer>
                <!-- <HYPgination v-model="pagination.page" :total="pagination.total"></HYPgination> -->
            </template>
        </el-card>
    </HYMain>
</template>


<style scoped>
.sel-margin-bottom {
    /* margin-bottom: 20px; */
    margin-right: 20px;
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

/* .gantrypsaminfot-table .ellipsis-column .cell {
    white-space: nowrap;
    overflow: hidden;
     
    text-overflow: ellipsis;
} */

/* 表格标题加粗 */
.bold-title {
    font-weight: bold;
}

.vertical-divider {
    display: inline-block;
    width: 2px;
    /* 竖线的宽度 */
    height: 30px;
    /* 竖线的高度，可以根据需要调整 */
    margin: 0 10px;
    /* 左右间距，可以根据需要调整 */
    background-color: #cccccc;
    /* 竖线的颜色，可以根据需要调整 */
    vertical-align: middle;
    /* 使竖线垂直居中 */
}
</style>