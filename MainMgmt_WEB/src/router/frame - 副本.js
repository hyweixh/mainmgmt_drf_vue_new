import frame from '@/views/frame/frame.vue';
import home from '@/views/home/home.vue';
import sys from '@/views/auth/index.vue';
import user from '@/views/auth/userInfo/userInfo.vue';
import role from '@/views/auth/roleInfo/roleInfo.vue';
import menu from '@/views/auth/menuInfo/menuInfo.vue';
import Forbidden from '@/views/error/401.vue';
import requestLog from '@/views/auth/requestLog/requestLog.vue';
import deviceList from '@/views/devicemgmt/list.vue';  // ✅ 导入设备列表
import devicemgmt_add from '@/views/devicemgmt/add.vue';
import devicemgmt_edit from '@/views/devicemgmt/edit.vue'; 
import checklanesoftList from '@/views/checklanesoft/checklanesoft_list.vue';
import VehlossrateList from '@/views/vehlossrate/vehlossrate_list.vue'
import vehlossrate_disppic from '@/views/vehlossrate/vehlossrate_disppic.vue'
import holidayfreelist from '@/views/holidayfree/holidayfree_list.vue'
import lanepsaminfolist from '@/views/lanepsaminfo/lanepsaminfo_list.vue'
import gantrypsaminfolist from '@/views/gantrypsaminfo/gantrypsaminfo_list.vue'
const routes = [
  {
    path: '/',
    name: 'frame',
    component: frame,
    meta: { text: '框架' },
    children: [
      {
        path: '/',
        name: 'home',
        component: home,
        meta: { text: '主页', icon: 'home' }
      },
      // 设备管理菜单
      {
        path: '/devicemgmt',
        name: 'devicemgmt',
        redirect: '/devicemgmt/list',
        meta: { text: '设备管理', icon: 'app' },
        children: [
          {
            path: 'list',
            name: 'devicemgmt_list',
            component: deviceList,
            meta: { text: '设备列表', icon: 'server' }
          },
          {
            path: 'devices',  // ✅ 相对路径
            name: 'devicemgmt_add',
            component: devicemgmt_add,
            meta: { 
              text: '添加设备信息',
              permission: 'devices:add'  // ✅ 必须放在 meta 内部
            },
            props: true
          },  
          {
            path: 'devices/:id',  // ✅ 相对路径
            name: 'devicemgmt_edit',
            component: devicemgmt_edit,
            meta: { 
              text: '编辑设备信息',
              permission: 'devices:edit'  // ✅ 必须放在 meta 内部
            },            
            props: true
          },
          {
            path: 'upload',  // ✅ 相对路径
            name: 'devices-upload',
            // component: devicemgmt_edit,
            meta: { 
              text: '批量上传',
              permission: 'devices:upload'  // ✅ 必须放在 meta 内部
            },            
            props: true
          }
          
        ]
      },
      // 车道软件检查菜单
      {
        path: '/checklanesoft',
        name: 'checklanesoft',
        redirect: '/checklanesoft/list',
        meta: { text: '收费系统', icon: 'app' },
        children: [
          {
            path: 'list',
            name: 'checklanesoft_list',
            component: checklanesoftList,
            meta: { text: '车道软件信息', icon: 'server' }
            
          },   
 
        ]
      },
      // 车牌识别率菜单
      {
        path: '/vehlossrate',
        name: 'vehlossrate',
        redirect: '/vehlossrate/list',
        meta: { text: '车牌识别率', icon: 'app' },
        children: [
          {
            path: 'list',
            name: 'vehlossrate_list',
            component: VehlossrateList,
            meta: { text: '车牌识别列表', icon: 'server' }            
          },   
          {
            path: 'disppic',  // ✅ 建议同步修改路径，保持一致性
            name: 'vehlossrate_disppic',  // ✅ 改为与跳转名称一致
            component: vehlossrate_disppic,
            meta: { 
              text: '获取车辆图像', 
              // icon: 'server' ,  
              permission: 'vehlossrate:getimageurl' 
            }       
          },   
        ]
      },
      // 节假日免费参数
      {
        path: '/holidayfree',
        name: 'holidayfree',
        redirect: '/holidayfree/list',
        meta: { text: '节假日免费参数', icon: 'app' },
        children: [
          {
            path: 'list',
            name: 'holidayfree_list',
            component: holidayfreelist,
            meta: { text: '节假日免费参数', icon: 'server' }            
          },       
        ]
      },
      // 车道psam卡信息
      {
        path: '/lanepsaminfo',
        name: 'lanepsaminfo',
        redirect: '/lanepsaminfo/list',
        meta: { text: '车道psam卡信息', icon: 'app' },
        children: [
          {
            path: 'list',
            name: 'lanepsaminfo_list',
            component: lanepsaminfolist,
            meta: { text: '车道psam卡信息', icon: 'server' }            
          },     
          {
            path: '/getlanepsaminfo',
            name: 'getlanepsaminfo',
            // component: ,
            meta: { 
              text: '获取车道psam卡信息', 
              // icon: 'server' ,
              permission: 'lanepsaminfo:getpsam' 
            }            
          },   
          {
            path: '/lanepsaminfo/:psamno',
            name: 'editLanepsam',
            // component: ,
            meta: { 
              text: '编辑psam卡信息', 
              // icon: 'server' ,
             permission: 'lanepsaminfo:edit' 
            }            
          },       
          // 下载车道psam卡信息
          {
            path: '/lanepsaminfo/download',
            name: 'downloadLanepsam',
            // component: ,
            meta: { 
              text: '下载psam卡信息', 
              // icon: 'server' ,
              permission: 'lanepsaminfo:download'
            }            
          },     
        ]
      },
      // 门架psam卡信息
      {
        path: '/gantrypsaminfo',
        name: 'gantrypsaminfo',
        redirect: '/gantrypsaminfo/list',
        meta: { text: '门架psam卡信息', icon: 'app' },
        children: [
          {
            path: 'list',
            name: 'gantrypsaminfo_list',
            component: gantrypsaminfolist,
            meta: { text: '门架psam卡信息', icon: 'server' }            
          },     
          {
            path: '/getlanepsaminfo',
            name: 'getlanepsaminfo',
            // component: ,
            meta: { 
              text: '获取车道psam卡信息', 
              // icon: 'server' ,
              permission: 'lanepsaminfo:getpsam' 
            }            
          },   
          {
            path: '/lanepsaminfo/:psamno',
            name: 'editLanepsam',
            // component: ,
            meta: { 
              text: '编辑psam卡信息', 
              // icon: 'server' ,
             permission: 'lanepsaminfo:edit' 
            }            
          },       
          // 下载车道psam卡信息
          {
            path: '/lanepsaminfo/download',
            name: 'downloadLanepsam',
            // component: ,
            meta: { 
              text: '下载psam卡信息', 
              // icon: 'server' ,
              permission: 'lanepsaminfo:download'
            }            
          },     
        ]
      },
      // 系统管理菜单
      {
        path: '/sys',
        name: 'sys',
        component: sys,
        children: [
          { path: 'user', name: 'user', component: user },
          { path: 'role', name: 'role', component: role },
          { path: 'menu', name: 'menu', component: menu },
          { path: 'requestLog', name: 'requestLog', component: requestLog, meta: { text: '审计日志', icon: 'Redis' } }
        ]
      },
      { path: '/Forbidden', name: 'Forbidden', component: Forbidden }
    ]
  }
];

export default routes;

// 以下是调试信息
// frame.js 最底部
// console.log('📦 路由配置检查');
// const devicemgmtRoute = routes[0].children.find(r => r.name === 'devicemgmt');
// const addRoute = devicemgmtRoute?.children?.find(c => c.name === 'devicemgmt_add');
// console.log('devicemgmt_add 路由对象:', addRoute);
// console.log('meta.permission 值:', addRoute?.meta?.permission);