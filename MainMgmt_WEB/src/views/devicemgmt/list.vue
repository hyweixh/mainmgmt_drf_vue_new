<script setup name="devicemgmt_list">
import { ref, reactive, onMounted, watch, computed } from "vue"
import devicemgmtHttp from "@/api/devicemgmtHttp";
import HYMain from "@/components/HYMain.vue";
import HYDialog from "@/components/HYDialog.vue";
import HYPgination from "@/components/HYPgination.vue";
import { useAuthStore } from "@/stores/auth";
import { useRouter } from "vue-router";
import { ElMessage, ElLoading } from 'element-plus'

const authStore = useAuthStore();

// 计算上传请求头
const uploadHeaders = computed(() => ({
  'Authorization': `Bearer ${authStore.token}`
}));

// 使用 useRouter 钩子来获取 router 实例  
const router = useRouter();

let deviceinfos = ref([])
let pagination = reactive({
    page: 1,
    total: 0
})
let page_size = ref() //每页记录数量，和后端一致

// 默认不显示对话框，ref基本类型
let dialogVisible = ref(false)
let copyPwdDialogVisible = ref(false)
let importdialogVisible = ref(false)

// 过滤表单,reactive对象类型
let filterForm = reactive({
    subnetwork_id: null,
    devicetype_id: null,
    position: '',
    deviceip: '',
})

// 设备下标
let handleIndex = 0
let devicetypes = ref([]) // 设备类型
let subnettypes = ref([]) // 子网类型
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
        let data = await devicemgmtHttp.getDeviceinfoList(page, page_size, filterForm);
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
    try {
        let devicetype_data = await devicemgmtHttp.getDeviceType();
        let subnettype_data = await devicemgmtHttp.getSubnetType();
        devicetypes.value = devicetype_data;
        subnettypes.value = subnettype_data;
    } catch (error) {
        ElMessage.error('获取子网类型或设备类型信息失败!');
    }
})

// 监听分页是否有变化  
watch(() => pagination.page, async function (newPage) {
    requestDeviceinfos(newPage, page_size.value);
});

// 监听每页多少条记录的变化  
watch(page_size, async function (newSize) {
    if (pagination.page !== 1) {
        pagination.page = 1;
    }
    requestDeviceinfos(1, newSize);
});

const onSearch = () => {
    requestDeviceinfos(1, page_size.value);
}

const onEditDeviceInfo = (index) => {
    const device = deviceinfos.value[index];
    router.push({ name: 'devicemgmt_edit', params: { id: device.id } });
};

const ondeleteDeviceinfo = async () => {
    try {
        let deviceinfo = deviceinfos.value[handleIndex];
        if (!devicemgmtHttp || !devicemgmtHttp.deleteDeviceinfo) {
            throw new Error('devicemgmtHttp 或 deleteDeviceinfo 方法未定义');
        }
        await devicemgmtHttp.deleteDeviceinfo(deviceinfo.id)
        deviceinfos.value.splice(handleIndex, 1)
        dialogVisible.value = false;
        ElMessage.success("设备删除成功！")
    } catch (detail) {
        const errorMessage = detail && detail.message ? detail.message : '删除设备出错';
        ElMessage.error(errorMessage);
    }
}

const ondeleteDevCancel = () => {
    dialogVisible.value = false;
}

const onShowDialog = (index) => {
    handleIndex = index
    dialogVisible.value = true;
}

const onShowCopyPwdDialog = (index) => {
    const device = deviceinfos.value[index]
    currentDevice.value = device
    passpwds.pwd1 = device.pwd1_clear || ''
    passpwds.pwd2 = device.pwd2_clear || ''
    passpwds.pwd3 = device.pwd3_clear || ''
    passpwds.pwd4 = device.pwd4_clear || ''
    copyPwdDialogVisible.value = true
}

const onCopyPwd = async (user) => {
    const key = `pwd${user.slice(-1)}`
    const pwd = passpwds[key]
    if (!pwd) return ElMessage.warning('该用户密码为空')

    if (navigator.clipboard) {
        try {
            await navigator.clipboard.writeText(pwd)
            ElMessage.success('密码已复制到剪贴板')
        } catch (err) {
            console.error('复制失败:', err)
            ElMessage.error('复制失败，请手动复制')
        }
    } else {
        ElMessage.warning({
            message: `当前环境不支持自动复制\n请手动复制密码：${pwd}`,
            duration: 5000,
            showClose: true
        })
    }
    copyPwdDialogVisible.value = false
}

const onCpPwdCancel = () => {
    copyPwdDialogVisible.value = false
}

const onShowImportdeviceinfoDialog = () => {
    importdialogVisible.value = true;
}

// 导出数据
const export_deviceinfo = async () => {
    let rows = tableRef.value.getSelectionRows()
    if (!rows || rows.length == 0) {
        ElMessage.info('请先选中要导出的设备！')
        return;
    }
    
    try {
        let response = await devicemgmtHttp.downloadDeviceinfos(rows.map(row => row.id))
        let href = URL.createObjectURL(response.data)
        const a = document.createElement("a")
        a.href = href
        a.setAttribute('download', '设备信息.xlsx')
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(href)
    } catch (detail) {
        ElMessage.error(detail)
    }
}

// 批量上传
const uploadDialogVisible = ref(false)
const dialogUploadRef = ref(null)
const selectedFile = ref(null)
const uploading = ref(false)

// 文件选择回调
const handleFileSelect = (uploadFile) => {
    selectedFile.value = uploadFile.raw
}

// 重置上传表单
const resetUploadForm = () => {
    selectedFile.value = null
    dialogUploadRef.value?.clearFiles()
}

// 手动上传（在对话框内执行）
const handleManualUpload = async () => {
    if (!selectedFile.value) {
        ElMessage.warning('请先选择文件！')
        return
    }
    
    uploading.value = true
    const loading = ElLoading.service({
        lock: true,
        text: '正在解析并上传Excel文件...',
        background: 'rgba(0, 0, 0, 0.7)'
    })
    
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    
    try {
        await devicemgmtHttp.uploadDeviceinfo(formData)
        ElMessage.success('✅ 设备上传成功！')
        uploadDialogVisible.value = false
        requestDeviceinfos(1, page_size.value)
    } catch (error) {
        const detail = error.response?.data?.detail
        const errorMsg = detail || error.message || '未知错误，请联系管理员'
        console.error('【上传失败】', errorMsg)
        ElMessage({
            message: errorMsg,
            type: 'error',
            duration: 0,
            showClose: true,
            customClass: 'center-el-message'
        })
    } finally {
        uploading.value = false
        loading.close()
    }
}
</script>

<template>
    <HYDialog v-model="dialogVisible" title="提示" @submit="ondeleteDeviceinfo" @cancel="ondeleteDevCancel">
        <span>您确定要删除这个设备吗？</span>
    </HYDialog>

    <HYDialog v-model="copyPwdDialogVisible" title="拷贝密码" @submit="onCopyPwd(selectedAccount)" @cancel="onCpPwdCancel">
        <el-radio-group v-model="selectedAccount">
            <el-radio label="user1" :disabled="currentDevice.user1 === '无' || !currentDevice.user1">
                {{ currentDevice.user1 || '无' }}
            </el-radio>
            <el-radio label="user2" :disabled="currentDevice.user2 === '无' || !currentDevice.user2">
                {{ currentDevice.user2 || '无' }}
            </el-radio>
            <el-radio label="user3" :disabled="currentDevice.user3 === '无' || !currentDevice.user3">
                {{ currentDevice.user3 || '无' }}
            </el-radio>
            <el-radio label="user4" :disabled="currentDevice.user4 === '无' || !currentDevice.user4">
                {{ currentDevice.user4 || '无' }}
            </el-radio>
        </el-radio-group>
    </HYDialog>

    <HYMain title="设备列表" style="margin-top: 10px;">
        <el-card>
            <el-row>
                <el-col :span="8" class="d-flex justify-content-start">
                    <el-button 
                        v-permission="'devices:add'"
                        class="button_r" 
                        type="primary"
                        icon="Plus"
                        @click="$router.push('/devicemgmt/devices')">
                        新增设备
                    </el-button>
                    
                    <el-button 
                        v-permission="'devices:upload'"
                        class="button_r" 
                        type="primary" 
                        icon="Upload"
                        @click="uploadDialogVisible = true">
                        批量上传
                    </el-button>
                    
                    <el-button 
                        v-permission="'devices:download'" 
                        type="primary" 
                        icon="Download" 
                        @click="export_deviceinfo">
                        导出设备
                    </el-button>
                </el-col>
                
                <el-col :span="16" class="d-flex justify-content-end">
                    <el-form-item label="按子网">
                        <el-select v-model="filterForm.subnetwork_id" placeholder="请选择子网类型" class="select_with">
                            <el-option v-for="subnettype in subnettypes" :key="subnettype.id"
                                :label="subnettype.subnettypename" :value="subnettype.id" />
                        </el-select>
                    </el-form-item>
                    
                    <el-form-item label="按安装位置" class="input_with">
                        <el-input v-model="filterForm.position" placeholder="输入安装位置"/>
                    </el-form-item>
                    
                    <el-form-item label="按设备类型">
                        <el-select v-model="filterForm.devicetype_id" placeholder="请选择设备类型" class="select_with">
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
            <el-table :data="deviceinfos" ref="tableRef" class="devices-table">
                <el-table-column type="selection" width="55"></el-table-column>
                <el-table-column label="序号" width="60">
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
                <el-table-column prop="subnetwork.name" label="子网">
                    <template #default="scope">
                        {{ scope.row.subnetwork.subnettypename }}
                    </template>
                </el-table-column>
                <el-table-column prop="user1" label="用户1"></el-table-column>
                <el-table-column prop="user2" label="用户2"></el-table-column>
                <el-table-column prop="user3" label="用户3"></el-table-column>
                <el-table-column prop="user4" label="用户4"></el-table-column>
                <el-table-column label="操作" width="180">
                    <template #default="scope">
                        <el-button v-permission="'devices:edit'" type="primary" icon="Edit" circle @click="onEditDeviceInfo(scope.$index)"></el-button>
                        <el-button type="primary" icon="document-copy" circle @click="onShowCopyPwdDialog(scope.$index)"></el-button>
                        <el-button v-permission="'role:delete'" type="danger" icon="Delete" circle @click="onShowDialog(scope.$index)"></el-button>
                    </template>
                </el-table-column>
            </el-table>
            
            <template #footer>
                <HYPgination v-model="pagination.page" :total="pagination.total"></HYPgination>
            </template>
        </el-card>
    </HYMain>

    <!-- 上传对话框 -->
    <el-dialog 
        v-model="uploadDialogVisible" 
        title="批量上传设备" 
        width="500px"
        @closed="resetUploadForm">
        
        <el-form-item label="选择Excel文件：">
            <el-upload
                ref="dialogUploadRef"
                :auto-upload="false"
                :on-change="handleFileSelect"
                :show-file-list="false"
                accept=".xlsx">
                <el-button type="primary" icon="Folder">浏览文件</el-button>
            </el-upload>
            
            <div v-if="selectedFile" style="margin-top: 10px; padding: 8px; background: #f0f9ff; border-radius: 4px;">
                <el-icon style="color: #67C23A; margin-right: 5px;"><SuccessFilled /></el-icon>
                <span style="color: #606266;">{{ selectedFile.name }}</span>
            </div>
        </el-form-item>
        
        <el-alert 
            title="请确保Excel文件包含Sheet1工作表，且列名格式正确" 
            type="info" 
            :closable="false"
            style="margin-top: 20px;">
        </el-alert>
        
        <template #footer>
            <el-button @click="uploadDialogVisible = false">取消</el-button>
            <el-button 
                type="success" 
                icon="Check"
                :disabled="!selectedFile"
                :loading="uploading"
                @click="handleManualUpload">
                开始上传
            </el-button>
        </template>
    </el-dialog>
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

.select_with {
    width: 150px;  
    margin-left: 10px;
    margin-right: 20px;
}

.button_r {
    margin-right: 20px;
}

.input_with {
    width: 250px;  
    margin-right: 20px;
}

/* 強制穿透所有層級 */
:deep(.el-form-item__label) {
    font-size: 16px !important;
    --el-form-label-font-size: 16px !important;
}
</style>