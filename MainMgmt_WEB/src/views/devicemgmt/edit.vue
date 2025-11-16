<script setup name="devicemgmt_edit">
import devicemgmtHttp from "@/api/devicemgmtHttp";
//import { ref, reactive, onMounted } from "vue"
import { ref, reactive, onMounted } from "vue"
import { ElMessage } from "element-plus"
// import timeFormatter from "@/utils/timeFormatter";
import HYMain from "@/components/HYMain.vue"
// import OAPagination from "@/components/OAPagination.vue"
import HYDialog from "@/components/HYDialog.vue";
import { useRoute, useRouter } from "vue-router"; 

const route = useRoute();  
const router = useRouter(); // 导入并使用 useRouter 

const labelPosition = 'right'; // 控制表单项标签的位置    
const inputWidth = 10;
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
        { pattern: ipRegex, message: '请输入正确的IP地址!', trigger: 'blur' }  
    ],  
    devicename: [{ required: true, message: "请输入设备名称！", trigger: 'blur' }],
    devicetype_id: [{ required: true, message: "请选择设备类型！", trigger: 'change' }],
    position: [{ required: true, message: "请输入安装位置！", trigger: 'blur' }],
    subnetwork_id: [{ required: true, message: "请选择子网类型！", trigger: 'change' }],
})

let formRef = ref()
// onMounted(async () => {
//     try {
//         let devicetype_data = await devicemgmtHttp.getDeviceType();
//         let subnettype_data = await devicemgmtHttp.getSubnetType();
//         devicetypes = devicetype_data;
//         subnettypes = subnettype_data;

//         const deviceId = route.params.id;
//         let response = await devicemgmtHttp.getDeviceDetail(deviceId);
//         /*
//             deviceinfoForm通过reactive，定义为响应式变量，如果给响应式变量重新赋值，会失去响应试功能。
//             通过Object.assign(deviceinfoForm, response);使用 Object.assign() 来更新 deviceinfoForm 
//         */        
//         Object.assign(deviceinfoForm, response);
//         // 如何获取当前的设备类型/子网类型？？？？？？？？？？？
//         // 提示devicetype.id错误，代码运行正常，忽略该提示
//         deviceinfoForm.devicetype_id = deviceinfoForm.devicetype.id;
//         deviceinfoForm.subnetwork_id = deviceinfoForm.subnetwork.id;
//         // console.log("deviceinfoForm data:",deviceinfoForm);  

//     } catch (error) {
//         // 添加更多的日志记录  
//         console.error("捕获到错误：", error);
//         console.error("错误的消息是：", error.message);
//         // 如果错误有堆栈信息，也打印出来  
//         if (error.stack) {
//             console.error("错误的堆栈信息是：", error.stack);
//         }
//         // 使用ElMessage显示错误信息  
//         ElMessage.error(error.message || "发生未知错误");
//     }
// });
onMounted(async () => {
  try {
    const [devicetype_data, subnettype_data] = await Promise.all([
      devicemgmtHttp.getDeviceType(),
      devicemgmtHttp.getSubnetType()
    ])
    devicetypes.value = devicetype_data
    subnettypes.value = subnettype_data

    const deviceId = route.params.id
    const res = await devicemgmtHttp.getDeviceDetail(deviceId)
    console.log("deviceId---",deviceId)

    /* ① 先把普通字段合并 */
    Object.assign(deviceinfoForm, res)

    /* ② 密码用明文字段回显 */
    deviceinfoForm.pwd1 = res.pwd1_clear || ''
    deviceinfoForm.pwd2 = res.pwd2_clear || ''
    deviceinfoForm.pwd3 = res.pwd3_clear || ''
    deviceinfoForm.pwd4 = res.pwd4_clear || ''

    /* ③ 外键 ID 单独赋 */
    deviceinfoForm.devicetype_id = res.devicetype.id
    deviceinfoForm.subnetwork_id = res.subnetwork.id
    // console.log('路由参数 deviceId:', route.params.id) // 应该显示数字ID
  } catch (e) {
    console.error(e)
    ElMessage.error(e.message || '加载失败')
  }
})
const onSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  /* ① 把整个 deviceinfoForm 交回去，保证 pwd1…4 都在 */
  const payload = { ...deviceinfoForm }   // 或者 toRaw(deviceinfoForm) 如果你用了 reactive
  console.log('提交载荷', payload)        // 调试：确认 pwd1…4 存在且是明文

  try {
    await devicemgmtHttp.editDeviceinfo(deviceinfoForm.id, payload)
    ElMessage.success('更新成功')
    router.back()
  } catch (e) {
    ElMessage.error(e?.message || '更新失败')
  }
}
const onCancel = async () => {
    // router.push({ name: 'devicemgmt_list' });
    router.back(); // 返回上一个页面
}
</script>

<template>
    <HYMain title=编辑设备>
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
                            <el-select v-model="deviceinfoForm.devicetype_id">
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
                            <el-select v-model="deviceinfoForm.subnetwork_id" placeholder="请选择子网类型" >                                
                                <el-option v-for="type in subnettypes" :key="type.id" :label="type.subnettypename" :value="type.id">
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