import http from '../http'; // 导入已经封装好的 http 请求方法

const apiPrefix = '/api/CloudServer'; // 设置基础接口地址

// 获取所有中间件列表
const CloudServerInfo = (search,cloud_platform,page,size,params) => {
    params = params?params:{}
    params['search'] = search
    params['cloud_platform'] = cloud_platform
    // params['status'] = status
    params['page'] = page
    params['size'] = size
    return http.get(apiPrefix, params)
}

// 获取环境列表
const Platforms = () => {
    return http.get(apiPrefix+`/platforms`)
}

// 删除中间件
const CloudServerDelete = (id) => {
    const path = apiPrefix+`/`+id
    return http.delete(path)
}

// 更新中间件
const CloudServerUpdate = (id,data) => {
    const path = apiPrefix+`/`+id
    return http.put(path,data)
}

const CloudServerAdd = (data) => {
    return http.post(apiPrefix,data)
}

// 导出模板
const TemplateExport = () => {
  const path = apiPrefix + "/export-template"
  return http.downloadFile(path)
}

// 导出数据
const DateExport = () => {
  const path = apiPrefix + "/export-data"
  return http.downloadFile(path)
}



export default {
  CloudServerInfo,
  CloudServerDelete,
  Platforms,
  CloudServerUpdate,
  CloudServerAdd,
  TemplateExport,
  DateExport
}

