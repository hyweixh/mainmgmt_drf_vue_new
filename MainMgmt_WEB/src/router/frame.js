import frame from '@/views/frame/frame.vue';
import home from '@/views/home/home.vue';
import sys from '@/views/auth/index.vue';
import user from '@/views/auth/userInfo/userInfo.vue';
import role from '@/views/auth/roleInfo/roleInfo.vue';
import menu from '@/views/auth/menuInfo/menuInfo.vue';
import Forbidden from '@/views/error/401.vue';
import requestLog from '@/views/auth/requestLog/requestLog.vue';
import deviceList from '@/views/devicemgmt/list.vue';
import devicemgmt_add from '@/views/devicemgmt/add.vue';
import devicemgmt_edit from '@/views/devicemgmt/edit.vue';
import checklanesoftList from '@/views/checklanesoft/checklanesoft_list.vue';
import VehlossrateList from '@/views/vehlossrate/vehlossrate_list.vue';
import vehlossrate_disppic from '@/views/vehlossrate/vehlossrate_disppic.vue';
import holidayfreelist from '@/views/holidayfree/holidayfree_list.vue';
import lanepsaminfolist from '@/views/lanepsaminfo/lanepsaminfo_list.vue';
import gantrypsaminfolist from '@/views/gantrypsaminfo/gantrypsaminfo_list.vue';

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
            meta: { text: '设备列表', icon: 'server', permission: 'devices:view' }
          },
          {
            path: 'devices',
            name: 'devicemgmt_add',
            component: devicemgmt_add,
            meta: { 
              text: '添加设备信息',
              permission: 'devices:add'
            },
            props: true
          },
          {
            path: 'devices/:id',
            name: 'devicemgmt_edit',
            component: devicemgmt_edit,
            meta: { 
              text: '编辑设备信息',
              permission: 'devices:edit'
            },
            props: true
          },
          {
            path: 'upload',
            name: 'devices-upload',
            meta: { 
              text: '批量上传',
              permission: 'devices:upload'
            },
            props: true
          }
        ]
      },
      // 收费系统菜单
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
            meta: { text: '车道软件信息', icon: 'server', permission: 'checklanesoft:view' }
          },
          {
            path: '/api/checklanesoft/checklanesoft/:id',
            name: 'checklanesoft_edit',            
            meta: { text: '编辑故障信息', icon: 'server', permission: 'checklanesoft:edit' }
          }
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
            meta: { text: '车牌识别列表', icon: 'server', permission: 'vehlossrate:view' }
          },
          {
            path: 'disppic',
            name: 'vehlossrate_disppic',
            component: vehlossrate_disppic,
            meta: { 
              text: '获取车辆图像',
              permission: 'vehlossrate:getimageurl'
            }
          }
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
            meta: { text: '节假日免费参数', icon: 'server', permission: 'holidayfree:view' }
          }
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
            meta: { text: '车道psam卡信息', icon: 'server', permission: 'lanepsaminfo:view' }
          },
          {
            path: 'getpsam',
            name: 'getlanepsaminfo',
            meta: { 
              text: '获取车道psam卡信息',
              permission: 'lanepsaminfo:getpsam'
            }
          },
          {
            path: 'edit/:psamno',
            name: 'editLanepsam',
            meta: { 
              text: '编辑psam卡信息',
              permission: 'lanepsaminfo:edit'
            }
          },
          {
            path: 'download',
            name: 'downloadLanepsam',
            meta: { 
              text: '下载psam卡信息',
              permission: 'lanepsaminfo:download'
            }
          }
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
            meta: { text: '门架psam卡信息', icon: 'server', permission: 'gantrypsaminfo:view' }
          },
          {
            path: 'getpsam',
            name: 'getgantrypsaminfo',
            meta: { 
              text: '获取门架psam卡信息',
              permission: 'gantrypsaminfo:getpsam'
            }
          },
          {
            path: 'edit/:psamno',
            name: 'editGantrypsam',
            meta: { 
              text: '编辑门架psam卡信息',
              permission: 'gantrypsaminfo:edit'
            }
          },
          {
            path: 'download',
            name: 'downloadGantrypsam',
            meta: { 
              text: '下载门架psam卡信息',
              permission: 'gantrypsaminfo:download'
            }
          }
        ]
      },
      // 系统管理菜单
      {
        path: '/sys',
        name: 'sys',
        component: sys,
        meta: { text: '系统管理', icon: 'setting' },
        children: [
          { 
            path: 'user', 
            name: 'user', 
            component: user,
            meta: { text: '用户管理', permission: 'user:list' }
          },
          { 
            path: 'role', 
            name: 'role', 
            component: role,
            meta: { text: '角色管理', permission: 'role:list' }
          },
          { 
            path: 'menu', 
            name: 'menu', 
            component: menu,
            meta: { text: '菜单管理', permission: 'menu:list' }
          },
          { 
            path: 'requestLog', 
            name: 'requestLog', 
            component: requestLog, 
            meta: { text: '审计日志', icon: 'Redis' }
            // 注意：requestLog 在提供的权限列表中没有对应权限项
          }
        ]
      },
      { 
        path: '/Forbidden', 
        name: 'Forbidden', 
        component: Forbidden 
      }
    ]
  }
];

export default routes;