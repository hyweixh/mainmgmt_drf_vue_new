import http from '../http'; // 导入已经封装好的 http 请求方法

const apiPrefix = '/api/middleware'; // 设置基础接口地址

// 获取所有中间件列表
const middlewareInfo = (search,environment,page,size,params) => {
    params = params?params:{}
    params['search'] = search
    params['environment'] = environment
    params['page'] = page
    params['size'] = size
    return http.get(apiPrefix, params)
}

// 获取环境列表
const middlewareEnv = () => {
    return http.get(apiPrefix+`/environments`)
}

// 删除中间件
const middlewareDelete = (id) => {
    const path = apiPrefix+`/`+id
    return http.delete(path)
}

// 更新中间件
const middlewareUpdate = (id,data) => {
    const path = apiPrefix+`/`+id
    return http.put(path,data)
}

const middlewareAdd = (data) => {
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
  middlewareInfo,
  middlewareDelete,
  middlewareEnv,
  middlewareUpdate,
  middlewareAdd,
  TemplateExport,
  DateExport
}

