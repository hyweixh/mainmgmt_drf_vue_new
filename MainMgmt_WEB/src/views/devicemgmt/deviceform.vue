<script setup name="deviceform">
import OAMain from '@/components/HYMain.vue';
// import OADialog from '@/components/OADialog.vue';
import { ref, reactive, onBeforeUnmount, shallowRef, onMounted } from "vue"
// import '@wangeditor/editor/dist/css/style.css' // 引入 css
// import { Editor, Toolbar } from '@wangeditor/editor-for-vue'
import deviceinfoHttp from '@/api/devicemgmtHttp';
import { ElMessage } from "element-plus"
// import { useAuthStore } from '@/stores/auth';
// import informHttp from '@/api/informHttp';

const authStore = useAuthStore()

let deviceForm = reactive({
    title: '',
    content: '',
    department_ids: []
})
const rules = reactive({
    title: [{ required: true, message: "请输入标题！", trigger: 'blur' }],
    content: [{ required: true, message: "请输入内容！", trigger: 'blur' }],
    department_ids: [{ required: true, message: "请选择部门！", trigger: 'change' }]
})
let formRef = ref()
let formLabelWidth = "100px"
let departments = ref([])

////////////// 这是跟wangEditor相关的配置 //////////////
// 编辑器实例，必须用 shallowRef
const editorRef = shallowRef()

const toolbarConfig = {}
const editorConfig = {
    placeholder: '请输入内容...',
    MENU_CONF: {
        uploadImage: {
            // http://localhost:5173/image/upload
            // http://localhost:8000/image/upload
            server: import.meta.env.VITE_BASE_URL + '/image/upload',
            fieldName: 'image', //接收图片的字段
            maxFileSize: 0.5 * 1024 * 1024, //图片大小，与后端一至
            maxNumberOfFiles: 10,
            allowedFileTypes: ['image/*'],
            headers: {
                Authorization: "JWT " + authStore.token  //JWT后面+空格
            },
            timeout: 6 * 1000, // 6 秒,
            customInsert(res, insertFn) {
                if(res.errno == 0){
                    // res 即服务端的返回结果
                    let data = res.data;
                    let url = import.meta.env.VITE_BASE_URL + data.url
                    let href = import.meta.env.VITE_BASE_URL + data.href
                    let alt = data.alt;
                    // 从 res 中找到 url alt href ，然后插入图片
                    insertFn(url, alt, href)
                }else{
                    ElMessage.error(res.message)
                }
            },
            // 单个文件上传失败
            onFailed(file, res) {
                console.log(`${file.name} 上传失败`, res)
            },

            // 上传错误，或者触发 timeout 超时
            onError(file, err, res) {
                if(file.size > 0.5*1024*1024){
                    ElMessage.error('图片文件最大不能超过0.5MB!')
                }else{
                    ElMessage.error('图片格式不正确！')
                }
            },
        }
    }
}
// editorConfig.MENU_CONF['uploadImage']
let mode = "default"

// 组件销毁时，也及时销毁编辑器
onBeforeUnmount(() => {
    const editor = editorRef.value
    if (editor == null) return
    editor.destroy()
})

const handleCreated = (editor) => {
    editorRef.value = editor // 记录 editor 实例，重要！
}
////////////// 这是跟wangEditor相关的配置 //////////////

onMounted(async () => {
    try {
        let data = await staffHttp.getAllDepartment()
        departments.value = data.results
    } catch (detail) {
        ElMessage.error(detail)
    }
})

// 发布通知提交按钮功能
const onSubmit = () => {
    formRef.value.validate(async (valid, fields) => {
        if (valid) {
            console.log(informForm);
            try{
                let data = await informHttp.publishInform(informForm)
                console.log(data);
            }catch(detail){
                ElMessage.error(detail)
            }
        }
    })
}

</script>

<template>
    <OAMain title="添加设备">
        <el-card>
            <el-form :model="informForm" :rules="rules" ref="formRef">
                <el-form-item label="标题" :label-width="formLabelWidth" prop="title">
                    <el-input v-model="informForm.title" autocomplete="off" />
                </el-form-item>
                <el-form-item label="部门可见" :label-width="formLabelWidth" prop="department_ids">
                    <!-- multiple 选择多个部门 -->
                    <el-select multiple v-model="informForm.department_ids">
                        <el-option :value="0" label="所有部门"></el-option>
                        <el-option v-for="department in departments" :label="department.name" :value="department.id"
                            :key="department.name" />
                    </el-select>
                </el-form-item> 
                <el-form-item label="内容" :label-width="formLabelWidth" prop="content">
                    <div style="border: 1px solid #ccc; width: 100%;">
                        <Toolbar style="border-bottom: 1px solid #ccc" :editor="editorRef"
                            :defaultConfig="toolbarConfig" :mode="mode" />
                        <Editor style="height: 500px; overflow-y: hidden;" v-model="informForm.content"
                            :defaultConfig="editorConfig" :mode="mode" @onCreated="handleCreated" />
                    </div>
                </el-form-item>
                <el-form-item>
                    <!-- flex: 1;占父盒子的100%宽度 -->
                    <div style="text-align: right; flex: 1;">
                        <el-button type="primary" @click="onSubmit">提交</el-button>
                    </div>
                </el-form-item>
            </el-form>
        </el-card>
    </OAMain>
</template>

<style scoped></style>