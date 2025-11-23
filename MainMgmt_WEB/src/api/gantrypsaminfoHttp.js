import http from "./http" // 导入HTTP客户端模块，用于发起网络请求  

// 获取当前查询条件的所有记录
const get_filter_LanepsaminfoList = () => {
    const path = "/api/lanepsaminfo/getalllanepsaminfos"
    return http.downloadFile(path)
}  

// 从mysql中获取门架psamka信息list ，默认page=1
const getGantrypsaminfoList = (page, size, params) => {  
    // console.log("devicemgmtHttp--",page, size, params)
    const path = "/api/gantrypsaminfo/gantrypsaminfo" 
     // 如果params为空，返回一个空的对象，否则返回params
     params = params?params:{}
     params['page'] = page
     params['size'] = size
     // get方法中第二个参数为config，如果params不加{}，当作config参数    
    // console.log("path>>>>",path,{params})
    return http.get(path,params) // 调用HTTP GET请求， params不能加{}
}  

const editgantrypsam = (psamno, mem) => {    
    const path = `/api/gantrypsaminfo/gantrypsaminfo/${psamno}`;        
    // console.log("path>>>",path,"mem:",mem.value)
    const data = {  
        mem: mem.value // 假设后端期望的字段名是 'mem'  
    };  
    return http.patch(path, data);      
}

const get_gantrypsaminfo_frMSSQL = () => {    
    const path = '/api/gantrypsaminfo/getgantrypsaminfo';      
    return http.get(path);      
}


const downloadGantrypsaminfo = (pks) => {
    const path = "/api/gantrypsaminfo/download/"
    return http.downloadFile(path, {"pks": JSON.stringify(pks)})
}

export default {  
    getGantrypsaminfoList,
    editgantrypsam,  
    get_gantrypsaminfo_frMSSQL,
    downloadGantrypsaminfo,
}