<script setup name="devicemgmtcopypwd">

import devicemgmtHttp from "@/api/devicemgmtHttp";
//import { ref, reactive, onMounted } from "vue"
import { ref, reactive, onBeforeUnmount, shallowRef, computed,onMounted } from "vue"
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

let devicetypes = reactive({
    id: 1, 
    devicetypename: '服务器'
}); // 设备类型
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
   
})

let formRef = ref()


const onSubmit = async () => {  
    
    // devicetypes = devicetype_data;
    // subnettypes = subnettype_data;  
    formRef.value.validate(async (valid) => {  
        if (valid) {  
            try {                  
                await devicemgmtHttp.editDeviceinfo(deviceinfoForm);                 
                ElMessage.success( '更新设备成功！');  
                router.push({ name: 'devicemgmt_list' });  
            } catch (detail) {  
                // console.error(detail)
                ElMessage.error(detail);  
            }  
        }  
    });  
};  


</script>

<template>
     <HYDialog v-model="dialogVisible" title="提示" @submit="ondeleteDeviceinfo">
        <span>拷贝选定账号的密码</span>
    </HYDialog>
    
</template>

<style scoped>

</style>