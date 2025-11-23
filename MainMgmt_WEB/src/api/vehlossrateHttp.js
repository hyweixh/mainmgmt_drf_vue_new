import http from "./http" // 导入HTTP客户端模块，用于发起网络请求  

// 获取当前查询条件的所有记录
const get_filter_LanepsaminfoList = () => {
    const path = "/api/lanepsaminfo/getalllanepsaminfos"
    return http.downloadFile(path)
}  

// 从mysql中获取车牌识别信息list ，默认page=1
const getVehlossrateList = (page, size, params) => {  
    const path = "/api/vehlossrate/vehlossrate" 
     // 如果params为空，返回一个空的对象，否则返回params
     params = params?params:{}
     params['page'] = page
     params['size'] = size
    return http.get(path,params) // 调用HTTP GET请求， params不能加{}
}  
const get_vehlossrate_frMSSQL = (startime,endtime,NEVs) => {    
    const path = '/api/vehlossrate/getvehlossrate';  
    const data = {
        starttime:startime,
        endtime:endtime,
        is_NEVs:NEVs
    }    
    return http.get(path,data);      
}
const get_laneimage_url = (tollstationid,tolllaneid,laneno,starttime,endtime,is_NEVs) => {
    const path = '/api/vehlossrate/getimageurl'; 
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
    get_filter_LanepsaminfoList,
    get_vehlossrate_frMSSQL,
    get_laneimage_url,
    getVehlossrateList,

}