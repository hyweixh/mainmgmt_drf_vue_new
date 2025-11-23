// import { ref, computed } from 'vue'
import { defineStore } from 'pinia';  

export const useImageStore = defineStore('image', () => {
    // let _imageUrl = ref()
    function  setImageUrl(url) {  
        this.imageUrl = url;  
      }
    function  resetImageUrl() {  
        this.imageUrl = null;  
      }  
    return {setImageUrl,resetImageUrl}  
})