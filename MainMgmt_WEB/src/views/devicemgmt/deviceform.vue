<!-- 新增设备和编辑设备公用一个form -->
<script setup name="devicemgmt_form">
import devicemgmtHttp from "@/api/devicemgmtHttp";
import { ref, reactive, onMounted, computed } from "vue"
import { ElMessage } from "element-plus"
import HYMain from "@/components/HYMain.vue"
import { useRoute, useRouter } from "vue-router";

const route = useRoute();
const router = useRouter();

// 模式判断：/device/form/add 或 /device/form/edit/:id
const isEdit = computed(() => route.params.mode === 'edit');
const pageTitle = computed(() => isEdit.value ? '编辑设备' : '新增设备');

const labelPosition = 'right';
const inputWidth = 10;

// 表单定义
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

// 下拉选项
let devicetypes = ref([])
let subnettypes = ref([])

// 验证规则
const ipRegex = /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
const rules = reactive({
  deviceip: [
    { required: true, message: "请输入IP!", trigger: 'blur' },
    { pattern: ipRegex, message: '请输入正确的IP地址！', trigger: 'blur' }
  ],
  devicename: [{ required: true, message: "请输入设备名称！", trigger: 'blur' }],
  devicetype_id: [{ required: true, message: "请选择设备类型！", trigger: 'change' }],
  position: [{ required: true, message: "请输入安装位置！", trigger: 'blur' }],
  subnetwork_id: [{ required: true, message: "请选择子网类型！", trigger: 'change' }],
})

const formRef = ref()

// 加载数据
onMounted(async () => {
  try {
    // 并行加载下拉选项
    const [devicetypeData, subnettypeData] = await Promise.all([
      devicemgmtHttp.getDeviceType(),
      devicemgmtHttp.getSubnetType()
    ]);
    devicetypes.value = devicetypeData;
    subnettypes.value = subnettypeData;

    // 编辑模式：加载设备详情
    if (isEdit.value) {
      const deviceId = route.params.id;
      if (!deviceId) {
        ElMessage.error('缺少设备ID');
        return;
      }
      
      const res = await devicemgmtHttp.getDeviceDetail(deviceId);
      
      // 合并基础数据
      Object.assign(deviceinfoForm, res);
      
      // 处理密码字段（假设后端返回 pwd1_clear 等明文字段）
      deviceinfoForm.pwd1 = res.pwd1_clear || '';
      deviceinfoForm.pwd2 = res.pwd2_clear || '';
      deviceinfoForm.pwd3 = res.pwd3_clear || '';
      deviceinfoForm.pwd4 = res.pwd4_clear || '';
      
      // 设置外键ID
      deviceinfoForm.devicetype_id = res.devicetype?.id || '';
      deviceinfoForm.subnetwork_id = res.subnetwork?.id || '';
    }
  } catch (error) {
    console.error("加载失败：", error);
    ElMessage.error(error.message || "加载失败");
  }
});

// 提交处理
const onSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false);
  if (!valid) return;

  try {
    const payload = { ...deviceinfoForm };
    
    if (isEdit.value) {
      // 编辑模式：需要传递ID
      await devicemgmtHttp.editDeviceinfo(route.params.id, payload);
      ElMessage.success('更新成功！');
    } else {
      // 新增模式
      await devicemgmtHttp.addDeviceinfo(payload);
      ElMessage.success('添加设备成功！');
    }
    
    router.back();
  } catch (error) {
    console.error("提交失败：", error);
    ElMessage.error(error.message || (isEdit.value ? "更新失败" : "添加失败"));
  }
};

// 取消
const onCancel = () => {
  router.back();
};
</script>

<template>
  <HYMain :title="pageTitle">
    <el-card>
      <el-form 
        :label-position="labelPosition" 
        label-width="100px" 
        :rules="rules" 
        :model="deviceinfoForm"
        ref="formRef" 
        class="flex-form"
      >
        <el-row>
          <el-col :span="12">
            <el-form-item label="设备名称" prop="devicename">
              <el-input v-model="deviceinfoForm.devicename" placeholder="请输入设备名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="设备类型" prop="devicetype_id">
              <el-select v-model="deviceinfoForm.devicetype_id" placeholder="请选择设备类型">
                <el-option 
                  v-for="type in devicetypes" 
                  :key="type.id" 
                  :label="type.devicetypename"
                  :value="type.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row>
          <el-col :span="12">
            <el-form-item label="安装位置" prop="position">
              <el-input v-model="deviceinfoForm.position" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="设备IP" prop="deviceip">
              <el-input v-model="deviceinfoForm.deviceip" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row>
          <el-col :span="12">
            <el-form-item label="所属子网" prop="subnetwork_id">
              <el-select v-model="deviceinfoForm.subnetwork_id" placeholder="请选择子网类型">
                <el-option 
                  v-for="type in subnettypes" 
                  :key="type.id" 
                  :label="type.subnettypename"
                  :value="type.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="设备厂商">
              <el-input v-model="deviceinfoForm.devicemanufacture" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row>
          <el-col :span="12">
            <el-form-item label="设备型号">
              <el-input v-model="deviceinfoForm.unittype" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="设备序列号">
              <el-input v-model="deviceinfoForm.deviceserialnumber" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row v-for="i in 4" :key="i">
          <el-col :span="12">
            <el-form-item :label="`用户${i}`">
              <el-input v-model="deviceinfoForm[`user${i}`]" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="`密码${i}`">
              <el-input v-model="deviceinfoForm[`pwd${i}`]" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row>
          <el-col :span="12">
            <el-form-item label="备注">
              <el-input type="textarea" v-model="deviceinfoForm.mem" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item>
          <el-button type="info" @click="onCancel">取消</el-button>
          <el-button type="primary" @click="onSubmit">提交</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </HYMain>
</template>

<style scoped>
.flex-form .el-row {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.flex-form .el-form-item {
  margin-bottom: 0;
}
</style>