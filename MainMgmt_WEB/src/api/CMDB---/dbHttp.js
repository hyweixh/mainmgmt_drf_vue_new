import http from '../http'; // 导入已经封装好的 http 请求方法

const apiPrefix = '/api/dbmanager'; // 设置基础接口地址

// 获取所有数据库列表
const DBInfo = (search,environment,page,size,params) => {
    params = params?params:{}
    params['search'] = search
    params['environment'] = environment
    params['page'] = page
    params['size'] = size
    return http.get(apiPrefix, params)
}

// 获取环境列表
const DBEnv = () => {
    return http.get(apiPrefix+`/environments`)
}

// 删除数据库
const DBDelete = (id) => {
    const path = apiPrefix+`/`+id
    return http.delete(path)
}

// 更新数据库
const DBUpdate = (id,data) => {
    const path = apiPrefix+`/`+id
    return http.put(path,data)
}

const DBAdd = (data) => {
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
  DBInfo,
  DBDelete,
  DBEnv,
  DBUpdate,
  DBAdd,
  TemplateExport,
  DateExport
}

