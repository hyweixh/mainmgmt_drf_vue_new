import http from "./http"

const getDeviceList = async () => {
    console.log('📡 调用getDeviceList')
    const data = await http.get("/api/pingdevices/devices/list")
    console.log('✅ 原始响应数据:', data)
    return data
}

// ✅ 修改：接收设备列表，同时发送IP列表和设备详情
const startBatchPing = async (devices) => {
    console.log('📡 调用startBatchPing, 设备数量:', devices.length)
    const ipList = devices.map(device => device.deviceip).filter(ip => ip)
    console.log('📦 请求体:', { ips: ipList, device_count: devices.length })
    const data = await http.post("/api/pingdevices/ping/batch", {
        ips: ipList,  // 发送IP列表供Celery任务使用
        devices: devices  // ✅ 同时发送设备详情供后续使用
    })
    console.log('✅ 任务启动响应:', data)
    return data
}

const getBatchPingProgress = async (taskId) => {
    console.log('📡 调用getBatchPingProgress, taskId:', taskId)
    const data = await http.get(`/api/pingdevices/ping/batch/${taskId}`)
    return data
}

const savePingResults = async (saveData) => {
    console.log('📡 调用savePingResults, 记录数量:', saveData.results?.length)
    console.log('📦 请求体:', saveData)
    const data = await http.post("/api/pingdevices/save-results", saveData)
    console.log('✅ 保存结果响应:', data)
    return data
}

// ✅ 修改：获取历史检查结果（无分页参数）
const getHistoricalResults = async () => {
    console.log('📡 调用getHistoricalResults（获取所有记录）')
    const data = await http.get("/api/pingdevices/results/history")
    console.log('✅ 历史数据响应:', data)
    return data
}

// 获取设备类型列表
export const getDeviceTypes = async () => {
    console.log('📡 调用getDeviceTypes（获取设备类型列表）')
    const data = await http.get("/api/devicemgmt/device-types")
    console.log('✅ 设备类型响应:', data)
    return data
}


export default {
    getDeviceList,
    startBatchPing,
    getBatchPingProgress,
    savePingResults,
    getHistoricalResults,
    getDeviceTypes
}

