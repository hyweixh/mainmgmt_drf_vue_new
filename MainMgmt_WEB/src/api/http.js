import axios from "axios"
import { useAuthStore } from "@/stores/auth";

class Http{
    constructor(){
        this.instance = axios.create({
            baseURL: import.meta.env.VITE_BASE_URL,
            timeout: 30000 
        });
        
        const PUBLIC_API_PATHS = [
            '/auth/login',
            '/auth/activate',
        ];
        
        this.instance.interceptors.request.use((config) => {
            const authStore = useAuthStore()
            const token = authStore.token
            
            const isPublicApi = PUBLIC_API_PATHS.some(path => 
                config.url.startsWith(path)
            );
            
            if(token && !isPublicApi){
                config.headers.Authorization = "JWT " + token  // ✅ 保持 JWT 前缀
            }
            return config
        })
    }
   
    post(path, data){
        return new Promise(async (resolve, reject) => {
            try{
                let result = await this.instance.post(path, data)
                resolve(result.data);
            }catch(err){
                reject(err)  // ✅ 修改这里
            }
        })
    }
   
    get(path, params){ 
        return new Promise(async (resolve, reject) => {
            try{
                let result = await this.instance.get(path, {params})
                resolve(result.data)
            }catch(err){
                reject(err)  // ✅ 修改这里
            }
        })
    }

    put(path, data) {  
        return new Promise(async (resolve, reject) => {  
            try {  
                let result = await this.instance.put(path, data);  
                resolve(result.data);  
            } catch (err) {  
                reject(err)  // ✅ 修改这里
            }  
        });  
    }

    patch(path, data) {  
        return new Promise(async (resolve, reject) => {  
            try {  
                let result = await this.instance.patch(path, data);  
                resolve(result.data);  
            } catch (err) {  
                reject(err)  // ✅ 修改这里
            }  
        });  
    } 

    delete(path){
        return new Promise(async (resolve, reject) => {
            try{
                let result = await this.instance.delete(path)
                resolve(result);
            }catch(err){
                reject(err)  // ✅ 修改这里
            }
        })
    }
    
    downloadFile(path, params){
        return new Promise(async (resolve, reject) => {
            try{
                let result = await this.instance.get(path, {
                    params,
                    responseType: "blob"
                })
                resolve(result)
            }catch(err){
                reject(err)  // ✅ 修改这里
            }
        })
    }
}

export default new Http()