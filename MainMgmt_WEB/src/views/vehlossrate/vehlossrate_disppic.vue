<script setup name="vehlossrate_disppic">  
import { ref, computed } from "vue";  
import { useRouter } from "vue-router"; // 导入 useRouter 而不是 useRoute  
//import { useRoute } from "vue-router"; 
import { useImageStore } from '@/stores/imageUrlStore'
// const route = useRoute();    

const router = useRouter(); // 使用 useRouter 获取路由实例  
const curIndex = ref(0); // 当前显示的图片索引 
// 从pinia获取imageUrl
const imageStore = useImageStore();  
const imageUrl = computed(() => imageStore.imageUrl);  
 
const onPreviousImage = () => {  
    curIndex.value = (curIndex.value - 1 + imageUrl.value.length) % imageUrl.value.length; // 循环遍历  
    // console.log("cur_imageUrl.value==", imageUrl.value[curIndex.value]);  
};  
  
const onNextImage = () => {  
    curIndex.value = (curIndex.value + 1) % imageUrl.value.length; // 循环遍历  
    // console.log("cur_imageUrl.value==", imageUrl.value[curIndex.value]);  
};  

const onGoBack = () => {  
    router.go(-1); // 返回上一页  
};  
  
const cur_imageUrl = computed(() => imageUrl.value[curIndex.value]); // 使用计算属性来获取当前图片 URL  
</script>  
  
<template>  
    <div class="parent" style="display: flex; justify-content: center; align-items: center; margin-top: 100px;">  
        <div class="image-container">  
            <img :src="cur_imageUrl">  
        </div>  
    </div>  
    <div class="button-container">    
        <el-button type="primary" @click="onGoBack">返回</el-button> <!-- 新增的返回按钮 -->  
        <el-button type="primary" :disabled="curIndex === 0" @click="onPreviousImage">前一张</el-button>    
        <!-- <el-button type="primary" :disabled="curIndex === imageUrl.value.length - 1" @click="onNextImage">后一张</el-button> -->
        <el-button type="primary" :disabled="curIndex === imageUrl.length - 1" @click="onNextImage">后一张</el-button>    
        <span style="color:green;font-size:20px;padding-left: 20px;">当前记录/总记录:    
            {{ curIndex + 1 }} / {{ imageUrl.length }}
        </span>    
    </div>    
    <div style="margin-top: 20px;">  
        <label style="display: flex; justify-content: center; align-items: center; color:green; font-size:20px;"  
               id="cur_lanepicurl_id">  
            当前url: {{ cur_imageUrl }}  
        </label>  
    </div>  
</template>  
<style scoped>  
  /* 设置图片容器的样式 */
  .image-container {
            justify-content: center; /* 水平居中 */
            /*align-items: center;  垂直居中 */
            width: 1000px;
            height: 750px;
            overflow: hidden;
            border: 1px solid #ccc;
            margin-bottom: 20px;
        }
       .image-container img {
            max-width: 100%;
            height: auto; /* 保留这个来保持图片的原始纵横比 */
            display: block; /* 确保图片作为块级元素显示，这样垂直居中就不需要了 */
        }

       .button-container {
            display: flex;
            justify-content: center; /* 水平居中按钮 */
            margin-top: 20px; /* 确保按钮始终在图片下方 */
        }

        .button-container button {
            margin: 0 10px;
        }
</style>