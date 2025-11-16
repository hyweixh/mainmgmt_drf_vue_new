import http from "../http"

// 获取vm
const vmInfo = (server_ip,project,env,ip,page,size,params) => {
    const path = "/api/vm"
    params = params?params:{}
    params['server_ip'] = server_ip
    params['project'] = project
    params['env'] = env
    params['ip'] = ip
    params['page'] = page
    params['size'] = size
    return http.get(path, params)
}

// 修改vm
const vmUpdate = (id,data) => {
    const path = "/api/vm/"+id
    return http.put(path,data)
}

// 新增vm
const vmAdd = (data) => {
    const path = "/api/vm"
    return http.post(path,data)
}

// 删除vm
const vmDelete = (id) => {
    const path = "/api/vm/"+id
    return http.delete(path)
}

// 获取vm 环境
const vmEnvInfo = () => {
    const path = "/api/vm/envs"
    return http.get(path)
}

// 获取vm 项目
const vmProjectInfo = () => {
    const path = "/api/project"
    return http.get(path)
}

// 更新vm 项目
const vmProjectUpdate = (id,data) => {
    const path = "/api/project/" + id
    return http.put(path,data)
}

// 新增vm 项目
const vmProjectCreate = (data) => {
    const path = "/api/project"
    return http.post(path,data)
}

// 删除vm 项目
const vmProjectDelete = (id) => {
    const path = "/api/project/"+id
    return http.delete(path)
}

// 导出vm
const vmExport = () => {
    const path = "/api/export/vm"
    return http.downloadFile(path)
}

// 导出vm模板
const vmTemplateExport = () => {
    const path = "/api/export/vm-template"
    return http.downloadFile(path)
}

export default{
    vmInfo,
    vmUpdate,
    vmAdd,
    vmDelete,
    vmEnvInfo,
    vmProjectInfo,
    vmProjectUpdate,
    vmProjectCreate,
    vmProjectDelete,
    vmExport,
    vmTemplateExport
}