<script setup name="devicemgmt_add">

import devicemgmtHttp from "@/api/devicemgmtHttp";
import { ref, reactive, onBeforeUnmount, shallowRef, computed,onMounted } from "vue"
import { ElMessage } from "element-plus"
// import timeFormatter from "@/utils/timeFormatter";
import HYMain from "@/components/HYMain.vue"
// import HYDialog from "@/components/HYDialog.vue";
import { useRoute, useRouter } from "vue-router";
  



const route = useRoute();  
const router = useRouter(); // 导入并使用 useRouter 

// const mode = computed(() => route.params.mode || 'add');  
// const isEdit = computed(() => mode.value === 'edit');  

const labelPosition = 'right'; // 控制表单项标签的位置    
const inputWidth = 10;  //10个栅格
const titleName = ref('windows_title'); 
let deviceinfoForm = reactive({
    deviceip: "",
    devicename: "",
    position: "",
    devicemanufacture: "",
    unittype: "",
    deviceserialnumber: "",
    user1: "",
    pwd1: "",
    user2: "",
    pwd2: "",
    user3: "",
    pwd3: "",
    user4: "",
    pwd4: "",
    mem: "",
    create_time: "",
    devicetype_id: "",
    subnetwork_id: ""
});

let devicetypes = ref([]) // 设备类型
let subnettypes = ref([]) // 子网类型

const ipRegex = /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;

const rules = reactive({
    deviceip: [  
        { required: true, message: "请输入IP!", trigger: 'blur' },  
        { pattern: ipRegex, message: '请输入正确的IP地址！', trigger: 'blur' }  
    ],  
    devicename: [{ required: true, message: "请输入设备名称！", trigger: 'blur' }],
    devicetype_id: [{ required: true, message: "请输入设备类型！", trigger: 'change' }],
    position: [{ required: true, message: "请输入安装位置！", trigger: 'blur' }],
    subnetwork_id: [{ required: true, message: "请选择子网类型！", trigger: 'change' }],
   
})

let formRef = ref()

onMounted(async () => {  
        // 加载设备类型和子网类型数据 
        try {  
           //  titleName.value ='添加设备';
            let devicetype_data = await devicemgmtHttp.getDeviceType();  
            let subnettype_data = await devicemgmtHttp.getSubnetType();  
            // devicetypes = devicetype_data.results;  //有分页情况
            // subnettypes = subnettype_data.results;   //有分页情况
            devicetypes.value = devicetype_data ; //无分页情况
            subnettypes.value = subnettype_data
            
            console.log("devicetypes--",devicetypes) 
        } catch (detail) {  
            ElMessage.error(detail);  
        }   
});  
  

const onSubmit = async () => {  
    formRef.value.validate(async (valid, fields) => {  
        if (valid) {  
            try {                   
                await devicemgmtHttp.addDeviceinfo(deviceinfoForm);                   
                ElMessage.success('添加设备成功！');  
                router.push({ name: 'devicemgmt_list' });  
            } catch (detail) {                   
               //  console.error("添加时发生错误：",response.data)             
                ElMessage.error(detail || "发生未知错误,检查后端或前端输入内容"); 
            }  
        }  
    });  
};  

const onCancel = async () => {
    // router.push({ name: 'devicemgmt_list' });
    router.back(); // 返回上一个页面
}
</script>

<template>
    <HYMain title = '新增设备'>
        <el-card>
            <el-form :label-position="labelPosition" label-width="100px" :rules="rules" :model="deviceinfoForm"
                ref="formRef" class="flex-form">
                <!-- <el-form :label-position="labelPosition" label-width="100px" :model="deviceinfo" class="flex-form"> -->
                <el-row>
                    <el-col :span="12">
                        <el-form-item label="设备名称" prop="devicename">
                            <el-input v-model="deviceinfoForm.devicename" placeholder="请输入设备名称"></el-input>
                        </el-form-item>
                    </el-col>
                    <el-col :span="12">                       
                        <el-form-item label="设备类型" prop="devicetype_id">
                            <el-select v-model="deviceinfoForm.devicetype_id" placeholder="请选择设备类型">
                                <el-option v-for="type in devicetypes" :key="type.id" :label="type.devicetypename"
                                    :value="type.id">
                                </el-option>
                            </el-select>
                        </el-form-item>
                    </el-col>
                </el-row>

                <el-row>
                    <el-col :span="12">
                        <el-form-item label="安装位置" prop="position">
                            <el-input v-model="deviceinfoForm.position"></el-input>
                        </el-form-item>
                    </el-col>

                    <el-col :span="12">
                        <el-form-item label="设备ip" prop="deviceip">
                            <el-input v-model="deviceinfoForm.deviceip"></el-input>
                        </el-form-item>
                    </el-col>
                </el-row>
                <el-row>
                    <el-col :span="12">
                        <el-form-item label="所属子网" prop="subnetwork_id">
                            <el-select v-model="deviceinfoForm.subnetwork_id" placeholder="请选择子网类型">
                                <el-option v-for="type in subnettypes" :key="type.id" :label="type.subnettypename"
                                    :value="type.id">
                                </el-option>
                            </el-select>
                        </el-form-item>
                    </el-col>
                    <el-col :span="12">
                        <el-form-item label="设备厂商">
                            <el-input v-model="deviceinfoForm.devicemanufacture"></el-input>
                        </el-form-item>
                    </el-col>
                </el-row>

                <el-row>
                    <el-col :span="12">
                        <el-form-item label="设备型号">
                            <el-input v-model="deviceinfoForm.unittype"></el-input>
                        </el-form-item>
                    </el-col>
                    <el-col :span="12">
                        <el-form-item label="设备序列号">
                            <el-input v-model="deviceinfoForm.deviceserialnumber"></el-input>
                        </el-form-item>
                    </el-col>
                </el-row>

                <el-row>
                    <el-col :span="12">
                        <el-form-item label="用户1">
                            <el-input v-model="deviceinfoForm.user1"></el-input>
                        </el-form-item>
                    </el-col>
                    <el-col :span="12">
                        <el-form-item label="密码1">
                            <el-input v-model="deviceinfoForm.pwd1"></el-input>
                        </el-form-item>
                    </el-col>
                </el-row>

                <el-row>
                    <el-col :span="12">
                        <el-form-item label="用户2">
                            <el-input v-model="deviceinfoForm.user2"></el-input>
                        </el-form-item>
                    </el-col>
                    <el-col :span="12">
                        <el-form-item label="密码2">
                            <el-input v-model="deviceinfoForm.pwd2"></el-input>
                        </el-form-item>
                    </el-col>
                </el-row>

                <el-row>
                    <el-col :span="12">
                        <el-form-item label="用户3">
                            <el-input v-model="deviceinfoForm.user3"></el-input>
                        </el-form-item>
                    </el-col>
                    <el-col :span="12">
                        <el-form-item label="密码3">
                            <el-input v-model="deviceinfoForm.pwd3"></el-input>
                        </el-form-item>
                    </el-col>
                </el-row>

                <el-row>
                    <el-col :span="12">
                        <el-form-item label="用户4">
                            <el-input v-model="deviceinfoForm.user4"></el-input>
                        </el-form-item>
                    </el-col>
                    <el-col :span="12">
                        <el-form-item label="密码4">
                            <el-input v-model="deviceinfoForm.pwd4"></el-input>
                        </el-form-item>
                    </el-col>
                </el-row>

                <el-row>
                    <el-col :span="12">
                        <el-form-item label="备注">
                            <el-input type="textarea" v-model="deviceinfoForm.mem"></el-input>
                        </el-form-item>
                    </el-col>
                    <!-- <el-col :span="12">
                        <el-form-item label="创建时间">
                            <el-input v-model="deviceinfoForm.create_time"></el-input>
                        </el-form-item>
                    </el-col> -->
                </el-row>
                <el-form-item>
                    <el-button type="info" @click="onCancel"> 取消 </el-button>  
                    <el-button type="primary" @click="onSubmit"> 提交 </el-button>
                </el-form-item>

                <!-- <el-form-item>
                  
                    <div style="text-align: right; flex: 1;">
                        <el-button>取消</el-button>
                        <el-button type="primary" @click="onSubmit">提交</el-button>
                    </div>
                </el-form-item>     -->
            </el-form>
        </el-card>

    </HYMain>
</template>

<style scoped>
.flex-form .el-row {
    display: flex;
    align-items: center;
    margin-bottom: 20px;
    /* 添加一些间距 */
}

.flex-form .el-form-item {
    margin-bottom: 0;
    /* 移除默认的底部边距 */
}
</style>