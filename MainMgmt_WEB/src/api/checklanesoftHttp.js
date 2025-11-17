import http from "./http" // 导入HTTP客户端模块，用于发起网络请求  

 
const get_lanesoftparams_frMSSQL = () => {    
    const path = '/api/checklanesoft/getchecklanesoft';    
    // const path = '/api/checklanesoft/checklanesoft';   
    return http.get(path);      
}
// 从mysql中获取车道软件参数list ，默认page=1
const getlanesoftparasList = (firm,page, size, params= {}) => {  
    const path = "/api/checklanesoft/checklanesoft?firm=" + firm      
     // 如果params为空，返回一个空的对象，否则返回params
     // params = params?params:{}
     params['page'] = page
     params['size'] = size 
    return http.get(path,params) // 调用HTTP GET请求， params不能加{}
}  

const download_checklanesoft = (selYM) => {
    try{
        const path = "/api/checklanesoft/download?selYM="+selYM
        return http.downloadFile(path)
    }catch (error) {          
       Element.error(error) 
    }  
    
}  

// 获取查询条件
const get_queryCondition = (querytype) => {  
    const path = "/api/checklanesoft/getquerycondition?queryType=" +  querytype  
    return http.get(path)
}  

// 更新故障描述、故障处理内容
const update_error_desc_proc = (id,error_desc,error_proc) => {    
    console.error('【调试】传入的id类型:', typeof id);
    console.error('【调试】传入的id值:', id);
    console.error('【调试】传入的id JSON:', JSON.stringify(id));
    
    const path = `/api/checklanesoft/checklanesoft/${id}`;    
    // console.log("path>>>",path,"mem:",mem.value)
    const data = {  
        error_desc: error_desc,
        error_proc: error_proc,
    };  
    return http.patch(path, data);      
}
// 确认记录
const confirm_checklanesoft = () => {    
    const path = `/api/checklanesoft/confirm`;      
    return http.post(path);      
}
  

export default {   
    get_lanesoftparams_frMSSQL,
    getlanesoftparasList,
    get_queryCondition,
    update_error_desc_proc,
    confirm_checklanesoft,
    download_checklanesoft,
}