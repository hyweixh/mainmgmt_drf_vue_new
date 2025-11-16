import http from "../http"

// 获取servers带过滤
const serversInfo = (location,ip,page,size,params) => {
    const path = "/api/servers"
    params = params?params:{}
    params['location'] = location
    params['ip'] = ip
    params['page'] = page
    params['size'] = size
    return http.get(path, params)
}

// 修改servers
const serversUpdate = (id,data) => {
    const path = "/api/servers/"+id
    return http.put(path,data)
}

// 新增servers
const serversAdd = (data) => {
    const path = "/api/servers"
    return http.post(path,data)
}

// 删除servers
const serversDelete = (id) => {
    const path = "/api/servers/"+id
    return http.delete(path)
}

// 获取servers 地点
const serversLocation = () => {
    const path = "/api/servers/location"
    return http.get(path)
}

// 导出servers
const serversExport = () => {
    const path = "/api/export/servers"
    return http.downloadFile(path)
}

// 导出servers模板
const serversTemplateExport = () => {
    const path = "/api/export/server-template"
    return http.downloadFile(path)
}



export default{
    serversInfo,
    serversUpdate,
    serversAdd,
    serversDelete,
    serversLocation,
    serversExport,
    serversTemplateExport,
}