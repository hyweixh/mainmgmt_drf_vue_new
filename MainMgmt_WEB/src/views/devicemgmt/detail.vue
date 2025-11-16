<script>
import { ElMessage } from 'element-plus';
import HYPageHeader from '@/components/HYPageHeader.vue';
import { ref, reactive, onMounted, watch } from "vue";
import devicemgmtHttp from "@/api/devicemgmtHttp";
import HYmain from '@/components/HYMain.vue';
import { useRoute } from "vue-router";

// 创建路由对象
const route = useRoute()

let deviceinfo = reactive({
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
    subnetwork_id: "",

})
onMounted(async () => {
    const pk = route.params.pk
    try {
        let data = await devicemgmtHttp.getDeviceDetail(pk)
        Object.assign(deviceinfo, data)
    } catch (detail) {
        ElMessage.error(detail)
    }
    // 发送阅读请求
    // await informHttp.readInform(pk)
})

</script>
<template >
    <HYMain title="设备详情">
        <el-card>
            <template #header>
                <h2>{{ deviceinfo.deviceip }}</h2>
            </template>
        </el-card>
    </HYMain>    
</template>
<style lang="">
    
</style>