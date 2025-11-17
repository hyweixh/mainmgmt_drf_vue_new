import http from "./http"
import axios from 'axios'; 
import { useAuthStore } from "@/stores/auth";

const BASE_PATH = "/api/devicemgmt"
// 获取设备列表
const getDeviceinfoList = (page, size, params = {}) => {
    params.page = page
    params.size = size
    return http.get(BASE_PATH + '/devices', params)  // GET /api/devicemgmt/devices
}

// 获取设备详情
const getDeviceDetail = (pk) => {
    return http.get(`${BASE_PATH}/devices/${pk}`)  // GET /api/devicemgmt/devices/8
}

// 添加设备信息
const addDeviceinfo = (data) => {
    return http.post(BASE_PATH + '/devices', data)  // POST /api/devicemgmt/devices
}

// 编辑设备信息
const editDeviceinfo = (pk, deviceInfo) => {
    return http.patch(`${BASE_PATH}/devices/${pk}`, deviceInfo)  // PATCH /api/devicemgmt/devices/8
}

// 删除设备信息
const deleteDeviceinfo = (pk) => {
    return http.delete(`${BASE_PATH}/devices/${pk}`)  // DELETE /api/devicemgmt/devices/8
}

// 获取设备类型
const getDeviceType = () => {
    return http.get(`${BASE_PATH}/device-types/`)  // 移除末尾 /
}

// 获取子网类型
const getSubnetType = () => {
    return http.get(`${BASE_PATH}/subnet-types/`)  // 移除末尾 /
}

// 解密密码
const getDecodePwd = (pwd) => {
    return http.post(`${BASE_PATH}/decrypt-password`, { decrypt_pwd: pwd })  // 移除末尾 /
}

// 下载设备信息
// ✅ 方案：使用原生 axios，确保 responseType 生效
// ✅ 修改：downloadDeviceinfos 接收 token 参数
// 在 devicemgmtHttp.js 中
const downloadDeviceinfos = (token, pks = []) => {
    const config = {
        method: 'GET',
        url: `${BASE_PATH}/devices/export/`,
        responseType: 'blob',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',  
        }
    };
    
    // 只在有选中设备时添加参数
    if (pks.length > 0) {
        config.params = { pks: JSON.stringify(pks) };
    }
    
    return axios(config);
}

export default {
    getDeviceinfoList,
    getDeviceDetail,
    addDeviceinfo,
    editDeviceinfo,
    deleteDeviceinfo,
    getDeviceType,
    getSubnetType,
    getDecodePwd,
    downloadDeviceinfos,
}