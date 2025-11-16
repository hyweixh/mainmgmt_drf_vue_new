import axios from "axios"
import { useAuthStore } from "@/stores/auth";

class Http{
    constructor(){
        this.instance = axios.create({
            // VITE_BASE_URL根据服务运行模式从开发或生产环境读取
            baseURL: import.meta.env.VITE_BASE_URL,
            // 单位为秒
            timeout: 6000 
        });
        
        // ==================== 白名单配置 ====================
        // 公共API路径：这些接口不需要 Token 认证
        const PUBLIC_API_PATHS = [
            // '/api/devicemgmt/subnettypes/',
            // '/devicemgmt/devicetypes',
            '/auth/login',
            '/auth/activate',
        ];
        // =================================================
        
        // 在请求头中带上token，config为回调函数的参数，保存配置信息
        this.instance.interceptors.request.use((config) => {
            const authStore = useAuthStore()
            const token = authStore.token
            // ✅ 判断当前请求是否在白名单中
            const isPublicApi = PUBLIC_API_PATHS.some(path => 
                config.url.startsWith(path)
            );
            
            // 只有非白名单接口才添加 Token
            if(token && !isPublicApi){
                config.headers.Authorization = "JWT " + token
            }
            return config
        })
    }
    // post方法
    // path: /auth/login
    // url: http://127.0.0.1:8000/auth/login
    // return this.instance.post(path, data)
    post(path, data){
        // return this.instance.post(path, data)
        return new Promise(async (resolve, reject) => {
            // await：网络请求发送出去后，线程会挂起这个等待
            // 等网络数据到达后，线程又会回到当前位置开始往后执行
            // 如果在某个函数中使用了await，那么这个函数就必须要定义成async
            // axios底层也是用的Promise对象，在响应的状态码不是200时，就会调用reject
            // 调用reject的结果是，外层的函数会抛出异常
            try{
                let result = await this.instance.post(path, data)
                // 如果走到下面代码，说明上面await函数没有抛出异常，就肯定说明返回的状态码是200
                resolve(result.data);
            }catch(err){
                // 走到catch中，就说明状态码肯定不是200
                try{
                    let detail = err.response.data.detail;
                    reject(detail)
                }catch{
                    reject('服务器端错误，请检查！')
                }
                
            }
        })
    }
   
    // get方法   
    //  get(path, params){ 
    get(path, params){ 
        return new Promise(async (resolve, reject) => {
            try{
                // {params}不加花括号params为当作config的参数，
                let result = await this.instance.get(path, {params})
                // console.log("http get data:",result.data)
                // console.log("path========",path)
                resolve(result.data)
            }catch(err){
                let detail = err.response ? err.response.data.detail : "发生未知错误";              
                reject(detail)
            }
        })
    }

    /**  
     * 发送一个 HTTP PUT 请求到指定的路径，并处理响应。  
     * @param {string} path - 请求的路径。  
     * @param {Object|string|FormData} data - 要发送的数据，可以是对象、字符串或FormData。  
     * @returns {Promise<any>} - 返回一个Promise，该Promise在请求成功时解析为响应的数据，在请求失败时拒绝并返回错误信息。  
     */  
    put(path, data) {  
        // 创建一个新的Promise对象，resolve和reject是Promise的解决和拒绝函数。  
        // async关键字允许我们在Promise的执行函数中使用await。  
        return new Promise(async (resolve, reject) => {  
            try {  
                // 使用await等待this.instance.put的异步结果。  
                // 假设this.instance是一个Axios实例或其他支持Promise的HTTP客户端。  
                // this.instance.put(path, data)发起PUT请求，并等待响应。  
                let result = await this.instance.put(path, data);  
                
                // 如果请求成功，从响应中提取数据并调用resolve函数，将数据作为成功的结果。  
                // 注意：这里假设响应对象有一个.data属性，它包含了实际的数据。  
                resolve(result.data);  
            } catch (err) {  
                // 如果在请求过程中发生错误（如网络问题、服务器错误等），  
                // 则捕获错误，并尝试从错误对象中提取更详细的错误信息。  
                // 假设错误对象有一个.response属性，且.response.data.detail包含了具体的错误信息。  
                let detail = err.response ? err.response.data.detail : '未知错误';  
                
                // 调用reject函数，将错误信息作为拒绝的原因。  
                reject(detail);  
            }  
        });  
    }

    patch(path, data) {  
        return new Promise(async (resolve, reject) => {  
            try {  
                let result = await this.instance.patch(path, data);  
                resolve(result.data);  
            } catch (err) {  
                let detail = err.response ? err.response.data.detail : '未知错误';  
                reject(detail);  
            }  
        });  
    } 

    // 删除对话框中，点击确定，删除设备
    delete(path){
        return new Promise(async (resolve, reject) => {
            try{
                let result = await this.instance.delete(path)
                // 因为服务端的delete方法，只是返回一个状态码，并没有数据，所以直接把result返回回去就可以了
                resolve(result);
            }catch(err){
                let detail = err.response.data.detail;
                reject(detail)
            }
        })
    }
    // 下载文件
    downloadFile(path, params){
        return new Promise(async (resolve, reject) => {
            try{
                let result = await this.instance.get(path, {
                    params,
                    // blob二进制大文件
                    responseType: "blob"
                })
                resolve(result)
            }catch(err){
                let detail = err.response.data.detail;
                reject(detail)
            }
        })
    }
}

export default new Http()