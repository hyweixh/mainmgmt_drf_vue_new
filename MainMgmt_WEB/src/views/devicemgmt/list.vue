<script setup name="devicemgmt_list">
import { ref, reactive, onMounted, watch } from "vue"
import devicemgmtHttp from "@/api/devicemgmtHttp";
import HYMain from "@/components/HYMain.vue";
import HYDialog from "@/components/HYDialog.vue";
import HYPgination from "@/components/HYPgination.vue";
// import timeFormatter from "@/utils/timeFormatter"
import { useAuthStore } from "@/stores/auth";
import { ElMessage } from "element-plus";
import { useRoute, useRouter } from "vue-router";
import { computed } from "vue";
const authStore = useAuthStore();

// 计算上传请求头
const uploadHeaders = computed(() => ({
  'Authorization': `Bearer ${authStore.token}`
}));

const BASE_URL = import.meta.env.VITE_BASE_URL
const route = useRoute();
// 使用 useRouter 钩子来获取 router 实例  
const router = useRouter();
// 定义方法  
function navigateToAddDevice() {
    // 使用 router 实例来导航到指定路径 
    title = "添加设备"
    router.push('/devicemgmt/add'); // 确保这个路径在你的路由配置中 
}

// const authStore = useAuthStore()

let deviceinfos = ref([])
let pagination = reactive({
    page: 1,
    total: 0
})
let page_size = ref() //每页记录数量，和后端一致

let title = "添加设备"
// 默认不显示对话框，ref基本类型
let dialogVisible = ref(false)
let copyPwdDialogVisible = ref(false)
let importdialogVisible = ref(false)
// 过滤表单,reactive对象类型
let filterForm = reactive({
    // null不选择任何子网
    subnetwork_id: null,
    devicetype_id: null,
    position: '',
    deviceip: '',
})
// 设备下标
let handleIndex = 0
let devicetypes = ref([]) // 设备类型
let subnettypes = ref([]) // 子网类型
let curr_page = ref()   //当前分页
let tableRef = ref()
const selectedAccount = ref('user1'); // 默认选择 user1  
// passpwds保存当前各账号的密码，在后续拷贝到剪切板时使用
const passpwds = reactive({
    pwd1: '',
    pwd2: '',
    pwd3: '',
    pwd4: '',
});
function resetFilterForm() {
    filterForm.subnetwork_id = null;
    filterForm.devicetype_id = null;
    filterForm.position = '';
    filterForm.deviceip = '';
}
const currentDevice = ref({});

async function requestDeviceinfos(page, page_size) {
    try {
        /*
        url中加入分页后获取的数据为:           
        count: 10
        next : "http://127.0.0.1:8000/devicemgmt/devicemgmt?page=2"
        previous: null
        results : (5) [{…}, {…}, {…}, {…}, {…}]
        [[Prototype]] :  Object
        */
        let data = await devicemgmtHttp.getDeviceinfoList(page, page_size, filterForm);
        // console.log('API Response:', data);
        let total = data.count;
        pagination.total = total;
        pagination.page = page
        deviceinfos.value = data.results;
    } catch (detail) {
        ElMessage.error(detail);
    }
}

onMounted(async () => {
    requestDeviceinfos(1, page_size.value)
    // console.log("路由传递参数：",route.query);
    try {
        let devicetype_data = await devicemgmtHttp.getDeviceType();
        let subnettype_data = await devicemgmtHttp.getSubnetType();
        devicetypes.value = devicetype_data;  // ✅ 正确：修改 ref 内部的值
        subnettypes.value = subnettype_data;  // ✅ 正确
        // console.log(' devicetypes====', devicetypes)
        // console.log('subnettypes=====',subnettypes)
        } catch (error) {
            // console.error('Error fetching data:', error);
            ElMessage.error('获取子网类型或设备类型信息失败!');

    }
})

// 监听分页是否有变化  
watch(() => pagination.page, async function (newPage) {
    // curr_page = newPage; //11-08
    requestDeviceinfos(newPage, page_size.value);
});

// 监听每页多少条记录的变化  
watch(page_size, async function (newSize) {
    // 如果当前不在第一页，重置为第一页  
    if (pagination.page !== 1) {
        pagination.page = 1;
    }
    // 请求新的数据  
    requestDeviceinfos(1, newSize);
});

const onSearch = (index) => {
    requestDeviceinfos(1, page_size.value);
}

const onEditDeviceInfo = (index) => {
    const device = deviceinfos.value[index];
    // console.log('点击了编辑按钮', { index, device, router });
    // 檢查路由是否存在
    const route = router.resolve({ name: 'devicemgmt_edit', params: { id: device.id } });
    console.log('目标路由:', route);
    
    router.push({ name: 'devicemgmt_edit', params: { id: device.id } });
};

const ondeleteDeviceinfo = async () => {
    try {
        let deviceinfo = deviceinfos.value[handleIndex];
        // console.log("devicemgmtHttp有：",devicemgmtHttp); // 调试输出，检查 devicemgmtHttp 对象  
        if (!devicemgmtHttp || !devicemgmtHttp.deleteDeviceinfo) {
            throw new Error('devicemgmtHttp 或 deleteDeviceinfo 方法未定义');
        }
        await devicemgmtHttp.deleteDeviceinfo(deviceinfo.id)
        deviceinfos.value.splice(handleIndex, 1) // 删除
        dialogVisible.value = false;
        ElMessage.success("设备删除成功！")
    } catch (detail) {
        // 检查 detail 和 detail.message 是否存在  
        const errorMessage = detail && detail.message ? detail.message : '删除设备出错';
        ElMessage.error(errorMessage);
    }
}

const ondeleteDevCancel = async () => {
    dialogVisible.value = false;
}

const onShowDialog = (index) => {
    handleIndex = index
    dialogVisible.value = true; //显示删除对话框
}

const onShowCopyPwdDialog = (index) => {
  const device = deviceinfos.value[index]
  currentDevice.value = device

  // 使用解密后的字段
  // device.pwd1_clear 是 undefined、null、"" 等假值，就赋空字符串 ''
  passpwds.pwd1 = device.pwd1_clear || ''
  passpwds.pwd2 = device.pwd2_clear || ''
  passpwds.pwd3 = device.pwd3_clear || ''
  passpwds.pwd4 = device.pwd4_clear || ''
  // console.log("当前pass--",passpwds.pwd1,passpwds.pwd2,passpwds.pwd3,passpwds.pwd4)
  copyPwdDialogVisible.value = true
}

const onCopyPwd = async (user) => {
  const key = `pwd${user.slice(-1)}` // 'user1' -> 'pwd1'
  const pwd = passpwds[key]
  if (!pwd) return ElMessage.warning('该用户密码为空')

  // 检测是否支持 Clipboard API
  if (navigator.clipboard) {
    // 现代浏览器（localhost 或 HTTPS）
    try {
      await navigator.clipboard.writeText(pwd)
      ElMessage.success('密码已复制到剪贴板')
    } catch (err) {
      console.error('复制失败:', err)
      ElMessage.error('复制失败，请手动复制')
    }
  } else {
    // 降级方案：显示密码让用户手动复制,生产环境不能这样做，用https
    ElMessage.warning({
      message: `当前环境不支持自动复制\n请手动复制密码：${pwd}`,
      duration: 5000, // 显示5秒，方便复制
      showClose: true
    })
  }

  copyPwdDialogVisible.value = false
}

const onCpPwdCancel = async () => {
    copyPwdDialogVisible.value = false
}
const onShowImportdeviceinfoDialog = (index) => {
    // const device = deviceinfos.value[index];  
    // handleIndex = device.id;  
    // currentDevice.value = device; // 使用 currentDevice.value 来存储当前设备信息  
    // console.log("当前记录--",device)
    importdialogVisible.value = true;

}
// 导出数据
const export_deviceinfo = async () => {
     // 用户选中的行
     let rows = tableRef.value.getSelectionRows()
    if(!rows || rows.length==0){
        ElMessage.info('请先选中要导出的设备！')
        return;
    }
    
    try{
        // let row_uids = []
        // for(let row of rows){
        //     row_uids.push(row.uid)
        // }
        // 上面的代码等同于下面的map
        let response = await devicemgmtHttp.downloadDeviceinfos(rows.map(row => row.id))
        // 借助a标签，将response数据，放到a标签的href属性上，然后模拟点击行为
        // 将返回的二进制数据，创建成一个url对象
        let href = URL.createObjectURL(response.data)
        // 创建a标签
        const a = document.createElement("a")
        a.href = href
        // 设置a标签的download属性，在点击的时候，就会执行下载操作
        a.setAttribute('download', '设备信息.xlsx')
        // 将a标签添加到网页结构中
        document.body.appendChild(a)
        // 模拟点击行为，只要点击了，那么浏览器就会启动下载操作（下载href属性指定的数据）
        a.click()

        // 只要执行了下载，a标签就没用了，就可以从网页中移除了
        document.body.removeChild(a)
        // 移除URL数据
        URL.revokeObjectURL(href)
    }catch(detail){
        ElMessage.error(detail)
    }
        
}
 

// const export_deviceinfo = async () => {
//   try {
//     const token = authStore.token
//     console.log("【调试】完整Token:", token)  // ✅ 查看完整Token
    
//     if (!token) {
//       ElMessage.error('未登录或Token失效，请重新登录')
//       return
//     }
    
//     // ✅ 检查Token格式是否正确（Bearer格式）
//     console.log("【调试】Token前20个字符:", token.substring(0, 20) + '...')
    
//     const selectedRows = tableRef.value?.getSelectionRows() || []
//     const pks = selectedRows.map(row => row.id)
//     console.log('导出设备ID列表:', pks)
    
//     const response = await devicemgmtHttp.downloadDeviceinfos(token, pks)
    
//     // ... 后续代码不变
    
//   } catch (error) {
//     console.error("【前端】导出失败:", error)
//     console.error("【调试】错误响应:", error.response)  // ✅ 查看后端返回的详细信息
//     ElMessage.error({
//       message: error.response?.data?.detail || '导出失败，请稍后重试',
//       duration: 5000,
//       showClose: true
//     })
//   }
// }
const onimportDeviceinfo = async () => {
    ElMessage.success('导入数据')
}
// 上传成功
const onUploadSuccess = () => {
    ElMessage.success("设备上传成功！")
    // 重新获取第一页的设备数据
    requestDeviceinfos(1, page_size.value)
}
// 上传失败
const onUploadFail = (error) => {
    const detail = JSON.parse(error.message).detail
    ElMessage.error(detail)
}

</script>

<template>
    <HYDialog v-model="dialogVisible" title="提示" @submit="ondeleteDeviceinfo" @cancel="ondeleteDevCancel">
        <span>您确定要删除这个设备吗？</span>
    </HYDialog>

    <HYDialog v-model="copyPwdDialogVisible" title="拷贝密码" @submit="onCopyPwd(selectedAccount)" @cancel="onCpPwdCancel">
        <el-radio-group v-model="selectedAccount">
            <el-radio label="user1" :disabled="currentDevice.user1 === '无' || !currentDevice.user1">{{
                currentDevice.user1 || '无' }}</el-radio>
            <el-radio label="user2" :disabled="currentDevice.user2 === '无' || !currentDevice.user2">{{
                currentDevice.user2 || '无' }}</el-radio>
            <el-radio label="user3" :disabled="currentDevice.user3 === '无' || !currentDevice.user3">{{
                currentDevice.user3 || '无' }}</el-radio>
            <el-radio label="user4" :disabled="currentDevice.user4 === '无' || !currentDevice.user4">{{
                currentDevice.user4 || '无' }}</el-radio>
        </el-radio-group>
    </HYDialog>
    <HYMain title="设备列表" style="margin-top: 10px;">
        <el-card>
            <el-row>
                <el-col :span="8" class="d-flex justify-content-start">
                    <!-- <el-button class="button_r" type="primary" icon="plus" @click="navigateToAddDevice">新增设备</el-button> -->
                    <el-button 
                        class="button_r" 
                        type="primary"
                        icon="Plus"
                        @click="$router.push('/devicemgmt/devices')">
                        新增设备
                    </el-button>
                    <el-form-item>
                        <el-upload 
                            @click="$router.push('/api/devicemgmt/upload')"
                            :headers="uploadHeaders"  
                            :on-success="onUploadSuccess"
                            :on-error="onUploadFail" 
                            :show-file-list="false" 
                            :auto-upload="true" accept=".xlsx">
                            <el-button class="button_r" type="primary" icon="Upload">批量上传</el-button>
                        </el-upload>
                    </el-form-item>
                    <el-form-item>
                        <el-button type="primary" icon="Download" @click="export_deviceinfo">导出设备</el-button>
                    </el-form-item>
                </el-col>
                <el-col :span="16" class="d-flex justify-content-end">
                    <el-form-item label="按子网">
                        <el-select v-model="filterForm.subnetwork_id" placeholder="请选择子网类型" class=select_with>
                            <el-option v-for="subnettype in subnettypes" :key="subnettype.id"
                                :label="subnettype.subnettypename" :value="subnettype.id" />
                        </el-select>
                    </el-form-item>
                    <el-form-item label="按安装位置" class="input_with">
                        <el-input v-model="filterForm.position"  placeholder="输入安装位置"/>
                    </el-form-item>
                    <el-form-item label="按设备类型">
                        <el-select v-model="filterForm.devicetype_id" placeholder="请选择设备类型" class=select_with>
                            <el-option v-for="devicetype in devicetypes" :key="devicetype.id"
                                :label="devicetype.devicetypename" :value="devicetype.id" />
                        </el-select>

                    </el-form-item>

                    <el-form-item label="按设备IP" class="input_with">
                        <el-input v-model="filterForm.deviceip" placeholder="输入设备IP"/>
                    </el-form-item>
                    <el-button type="primary" icon="Search" @click="onSearch"></el-button>
                    <el-button type="primary" icon="refresh-right" @click="resetFilterForm">重置</el-button>
                </el-col>
            </el-row>
        </el-card>
        <el-card>
            <!-- <el-table :data="deviceinfos" ref="tableRef" class="devices-table"> -->
            <el-table :data="deviceinfos" class="devices-table">    

                <el-table-column type="selection" width="55"></el-table-column>
                <el-table-column label="序号" width="60">
                     <!-- -- $index + 1：序号从1开始 -->
                    <template #default="scope">{{ scope.$index + 1 }}</template>
                </el-table-column>
                <el-table-column prop="deviceip" label="设备IP"></el-table-column>
                <el-table-column prop="devicename" label="设备名称"></el-table-column>
                <el-table-column prop="position" label="安装位置"></el-table-column>
                <el-table-column prop="devicetype.name" label="设备类型">
                    <template #default="scope">
                        {{ scope.row.devicetype.devicetypename }}
                    </template>
                </el-table-column>
                <!-- <el-table-column prop="devicemanufacture" label="设备厂商"></el-table-column>
                <el-table-column prop="unittype" label="设备型号"></el-table-column> -->
                <el-table-column prop="subnetwork.name" label="子网">
                    <template #default="scope">
                        {{ scope.row.subnetwork.subnettypename }}
                    </template>
                </el-table-column>
                <el-table-column prop="user1" label="用户1"></el-table-column>
                <!-- <el-table-column prop="pwd1" label="密码1"></el-table-column> -->
                <el-table-column prop="user2" label="用户2"></el-table-column>
                <!-- <el-table-column prop="pwd2" label="密码2"></el-table-column> -->
                <el-table-column prop="user3" label="用户3"></el-table-column>
                <!-- <el-table-column prop="pwd3" label="密码3"></el-table-column> -->
                <el-table-column prop="user4" label="用户4"></el-table-column>
                <!-- <el-table-column prop="pwd4" label="密码4"></el-table-column> -->

                <!-- <el-table-column prop="mem" label="备注" class-name="ellipsis-column"></el-table-column> -->
                <el-table-column label="操作">
                    <template #default="scope">
                        <el-button type="primary" icon="Edit" circle @click="onEditDeviceInfo(scope.$index)">
                        </el-button>
                        <el-button type="primary" icon="document-copy" circle
                            @click="onShowCopyPwdDialog(scope.$index)">
                        </el-button>
                        <el-button type="danger" icon="Delete" circle @click="onShowDialog(scope.$index)"></el-button>

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
.my-form-inline .el-input {
    --el-input-width: 140px;
}

/* 子网下拉框表单宽度 */
.my-form-inline .el-select {
    --el-select-width: 140px;
}

.my-form-inline .el-input {
    --el-input-width: 140px;
}


.el-badge {
    margin-right: 2px;
    margin-top: 2px;
}

.el-tag {
    margin-right: 2px;
}

.devices-table .ellipsis-column .cell {
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
        width:150px;  
        margin-left: 10px;
        margin-right: 20px;
    }
    .button_r {
        margin-right: 20px;
    }
    .input_with{
        width:250px;  
        margin-right: 20px;
    }
</style>
<style scoped>
    /* 強制穿透所有層級 
    不需要在 <el-form-item> 上做任何引用！:deep() 选择器会自动穿透作用域，
    所有 <el-form-item> 的 label 都会自动应用这个样式。
    */
    :deep(.el-form-item__label) {
    font-size: 16px !important;
    --el-form-label-font-size: 16px !important;
}
</style>