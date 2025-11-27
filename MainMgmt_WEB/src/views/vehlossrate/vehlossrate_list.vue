<script setup name="vehlossrate_list">
import { ref, reactive, onMounted, watch } from "vue"
import vehlossrateHttp from "@/api/vehlossrateHttp";
import HYMain from "@/components/HYMain.vue";
import HYPgination from "@/components/HYPgination.vue";
import timeFormatter from '@/utils/timeFormatter';
import { ElMessage } from "element-plus";
import { useRoute, useRouter } from "vue-router";
import { useImageStore } from '@/stores/imageUrlStore'
import { showLoading, hideLoading } from '@/utils/loading'

const BASE_URL = import.meta.env.VITE_BASE_URL
const route = useRoute();
// 使用 useRouter 钩子来获取 router 实例  
const router = useRouter();
 
// 从localStorage获取is_NEVs的值，如果不存在则默认为false  
const is_NEVs = ref(JSON.parse(localStorage.getItem('is_NEVs')) || false); 
 
 // const value1 = ref([]); 
 const value1 = ref(JSON.parse(localStorage.getItem('value1')) || []);

// let dialogVisible = ref(false)
let vehlossrates = ref([])
let pagination = reactive({
    page: 1,
    total: 0
})
let page_size = ref(10) //每页记录数量，和后端一致 
const pickerOptions = ref({}); // 默认情况下，pickerOptions 是空的  
  
// 过滤表单,reactive对象类型，per1:总识别率
let filterForm = reactive({
    stationno: null,  
    per1: null,       
})

 
let curr_page = ref()   //当前分页
let tableRef = ref()
let cur_laneinfo = reactive({
    stationid : '',
    tolllaneid : '',
    laneno:null,
    starttime : '',
    endtime: '', 
    is_NEVs:false, 
})

async function requestVehlossrate(page, page_size) {
    try {
        let data = await vehlossrateHttp.getVehlossrateList(page, page_size, filterForm);
        // console.log('API Response:', data);
        let total = data.count;
        pagination.total = total;
        pagination.page = page
        vehlossrates.value = data.results;       
    } catch (detail) {
        ElMessage.error(detail);
    }
}
const onSearch = (index) => {
    requestVehlossrate(1, page_size.value);
}

function resetFilterForm() {
    filterForm.stationno = null;
    filterForm.per1 = null;
}

onMounted(async () => {
    requestVehlossrate(1, page_size.value);   
})
// 监听日期选择框的变化，并保存到localStorage
watch(value1,(newVal) => {
    localStorage.setItem('value1', JSON.stringify(newVal)); 
});
// 监听is_NEVs的变化，并保存到localStorage  
watch(is_NEVs, (newVal) => {  
    localStorage.setItem('is_NEVs', JSON.stringify(newVal));  
});

// 监听分页是否有变化  
watch(() => pagination.page, async function (newPage) {
    curr_page.value = newPage;
    requestVehlossrate(newPage, page_size.value);
});

// 监听每页多少条记录的变化  
watch(page_size, async function (newSize) {
    // 如果当前不在第一页，重置为第一页  
    if (pagination.page !== 1) {
        pagination.page = 1;
    }
    // 请求新的数据  
    requestVehlossrate(1, newSize);
});

async function navigateToDisppic(index) {  
    cur_laneinfo.stationid = vehlossrates.value[index].stationid;  
    cur_laneinfo.tolllaneid = vehlossrates.value[index].tolllaneid;  
    cur_laneinfo.laneno = vehlossrates.value[index].laneno;  
    cur_laneinfo.starttime = vehlossrates.value[index].starttime;  
    cur_laneinfo.endtime = vehlossrates.value[index].endtime;  
    cur_laneinfo.is_NEVs = is_NEVs.value;

    try {  
        // 假设 get_laneimage_url 返回一个 Promise，该 Promise 解析为一个对象或 URL  
        // imageUrl获取的是对象，imageUrl.data取对象里的data值
        const imageUrl = await vehlossrateHttp.get_laneimage_url(  
            cur_laneinfo.stationid,  
            cur_laneinfo.tolllaneid,  
            cur_laneinfo.laneno,
            cur_laneinfo.starttime,  
            cur_laneinfo.endtime ,
            cur_laneinfo.is_NEVs,            
        ); 
        console.log("url长度",imageUrl) 
        // 保存到useImageUrlStore
        const imageStore = useImageStore(); 
        // 先清除原有的信息 
        imageStore.resetImageUrl()
        imageStore.setImageUrl(imageUrl.data); 
       
    //    router.push({name: 'vehlossrate_disppic',query: { imageUrl: imageUrl.data } }); 
    router.push({name: 'vehlossrate_disppic'});
    } catch (error) {  
        console.error('获取图像连接失败！:', error);  
    }  
}

const onSearch_vehlossrate = async () => {
  showLoading('正在查询，请等待...')
  try {
    const start_time = timeFormatter.stringFromDateTime(value1.value[0])
    const end_time   = timeFormatter.stringFromDateTime(value1.value[1])

    await vehlossrateHttp.get_vehlossrate_frMSSQL(start_time, end_time, is_NEVs.value)
    ElMessage.success('获取车牌识别率信息成功！')
    requestVehlossrate(1, page_size.value)
  } catch (error) {
    console.error('获取车牌识别率失败:', error)
    ElMessage.error('获取数据时发生错误，请稍后重试。')
  } finally {
    hideLoading() // ✅ 关键：关闭 loading
  }
}
// 格式化日期时间格式为“2025-11-27 00:00:00”,同时去掉时区
const formatDateTime = (row, column, cellValue) => {
  if (!cellValue) return '';
  return cellValue.replace('T', ' ').replace(/[+-]\d{2}:\d{2}$/, '');
}


</script>

<template>
    <HYMain title="车道车牌识别率" style="margin-top: 10px;">
        <el-card>
            <el-row>
                <el-col :span="12" class="d-flex justify-content-start">
                    <!-- align-items-center未能上下居中 -->
                    <span class="mr-20 font-size-14 align-items-center">请选择查询时段</span>
                    <el-date-picker 
                        class="date-picker-with"                         
                        v-model="value1" type="datetimerange"
                        start-placeholder="开始日期时间" 
                        end-placeholder="结束日期时间"                  
                        :picker-options="pickerOptions">                        
                    </el-date-picker>

                    <span class="mr-20 ml-20 font-size-14 align-items-center" >仅统计新能源车</span>
                    <el-switch class="sel-margin-bottom" 
                        v-model="is_NEVs" 
                        active-color="#13ce66"
                        inactive-color="#ff4949">
                    </el-switch>
                    <!-- 选择时间段后，执行按钮才可用   -->
                    <el-button class="ml-15" type="primary" :disabled="!(value1 && value1.length === 2 && value1[0] && value1[1])"
                        @click="onSearch_vehlossrate">执行</el-button>

                </el-col>
                <el-col :span="12" class="d-flex justify-content-end">
                    <el-form-item class="mr-20 font-size-14" label="按站编号" label-width="100px">
                        <el-input  v-model="filterForm.stationno"  placeholder="输入地标站编码" class="mr-20 font-size-14h"/>
                    </el-form-item>
                    <el-form-item class="mr-20 font-size-14" label="按总识别率" label-width="100px">
                        <el-input v-model="filterForm.per1" placeholder="小于/等于输入的值" class="imr-20 font-size-14"/>
                    </el-form-item>

                    <el-button type="primary" icon="Search" @click="onSearch"></el-button>
                    <el-button type="primary" icon="refresh-right" @click="resetFilterForm">重置</el-button>
                </el-col>
            </el-row>
        </el-card>

        <el-card>
            <el-table :data="vehlossrates" ref="tableRef" class="gantrypsaminfo-table">

                <!-- <el-table-column type="selection" width="55"></el-table-column> -->
                <el-table-column label="序号" width="60">
                    <!-- $index + 1：序号从1开始 -->
                    <template #default="scope">{{ scope.$index + 1 }}</template>
                </el-table-column>
                <!-- <el-table-column prop="tolllaneid" label="收费单元编号" width="200"></el-table-column>
                <el-table-column prop="stationid" label="国标站编码" width="150"></el-table-column> -->
                <el-table-column prop="stationno" label="站编码" width="70"></el-table-column>
                <el-table-column prop="laneno" label="车道编码" width="100"></el-table-column>
                <el-table-column prop="lanetypename" label="车道类型" width="120"></el-table-column>
                <el-table-column prop="lanecomputerip" label="车道IP" width="130"></el-table-column>
                <el-table-column prop="cnt" label="交易总数" width="100"></el-table-column>
                <el-table-column prop="veh" label="抓拍数量" width="100"></el-table-column>
                <el-table-column prop="scu" label="识别数量" width="100"></el-table-column>
                <el-table-column prop="per" label="抓拍率%" width="100"></el-table-column>
                <el-table-column prop="per1" label="总识别率%" width="100"></el-table-column>
                <el-table-column prop="per2" label="有牌识别率%" width="150"></el-table-column>
                <el-table-column prop="starttime" label="统计开始时间" width="200" :formatter="formatDateTime">

                </el-table-column>
                <el-table-column prop="endtime" label="统计结束时间" width="200" :formatter="formatDateTime">

                </el-table-column>
                <!-- <el-table-column prop="inspector" label="检查人员" width="120"></el-table-column> -->
                <!-- <el-table-column prop="inspecttime" label="检查时间" width="180"></el-table-column> -->
                <el-table-column label="操作">
                    <template #default="scope">
                        <el-button type="primary" icon="picture" circle @click="navigateToDisppic(scope.$index)">
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
/* 移除重复的样式，只保留组件特有的样式 */
.lanepsaminfot-table .ellipsis-column .cell {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.bold-title {
  font-weight: bold;
}
/* 标准日期选择器宽度 */
.date-picker-with {
  width: 360px; /* 适合日期时间范围选择器的默认宽度 */
  font-size: 14px
}                      

</style>