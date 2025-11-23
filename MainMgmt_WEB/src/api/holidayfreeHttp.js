import http from "./http" // 导入HTTP客户端模块，用于发起网络请求  

// 获取当前查询条件的所有记录
const get_filter_LanepsaminfoList = () => {
    const path = "/lanepsaminfo/getalllanepsaminfos"
    return http.downloadFile(path)
}  

// 从mysql中获取门架psamka信息list ，默认page=1
const getholidayfreeList = (page, size, params) => {  
    const path = "/api/holidayfree/holidayfree" 
     // 如果params为空，返回一个空的对象，否则返回params
     params = params?params:{}
     params['page'] = page
     params['size'] = size
    return http.get(path,params) // 调用HTTP GET请求， params不能加{}
}  



const get_holidayfree_frlane = (startime,endtime,NEVs) => {    
    const path = '/api/holidayfree/update';     
    return http.get(path);      
}

const get_laneimage_url = (tollstationid,tolllaneid,laneno,starttime,endtime,is_NEVs) => {
    const path = 'vehlossrate/getimageurl'; 
    const data = {
        tollstationid:tollstationid,
        tolllaneid:tolllaneid,
        laneno:laneno,
        starttime:starttime,
        endtime:endtime,
        is_NEVs:is_NEVs       
    } 
    return http.get(path,data);  
}

export default {  
    get_holidayfree_frlane,
    getholidayfreeList,

}