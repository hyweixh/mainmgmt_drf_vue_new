import { createApp } from 'vue'
import { createPinia } from 'pinia'

//iconPark
// import '@icon-park/vue-next/styles/index.css';

//ElementPlus插件
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css' //暗黑模式
// 中文
import zhCn from 'element-plus/es/locale/lang/zh-cn'

// 图标
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

// 完整导入 表格库
import VxeUITable from 'vxe-table'
import 'vxe-table/lib/style.css'
import '@/assets/css/utilities.css'  
import 'virtual:svg-icons-register' //注册svg脚本
import globalComponent from '@/components/install.js'
import App from './App.vue'
import router from './router'
import 'nprogress/nprogress.css'
import 'animate.css'
import "amfe-flexible/index.js";  //rem布局
/* 1. 引入指令（跟你已有的别的导出互不影响） */
import { permission } from '@/utils/permission'
const app = createApp(App)

/* 2. 注册全局指令 */
app.directive('permission', permission)
//注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(createPinia())
app.use(router)
app.use(ElementPlus, {
  locale: zhCn
})


app.mount('#app')
app.use(VxeUITable) // 注册VxeUITable
app.use(globalComponent)
