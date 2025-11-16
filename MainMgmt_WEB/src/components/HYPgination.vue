<script setup name="HYPagination">
// import {defineModel, defineProps} from "vue"

let props = defineProps({
    total: {
        type: Number,
        default: 0
    },
    pageSize: {
        type: Number,
        default: 15  //每页15条记录
    }
})

let page = defineModel({required: true})

</script>

<template>
       <div class="pagination-container">  
        <el-pagination  
            background  
            layout="prev, pager, next"  
            :total="props.total"  
            :page-size="props.pageSize"  
            v-model:current-page="page"  
        />  
        <span class="total-records">记录总数：{{ props.total }}</span>  
    </div> 
</template>

<style scoped>  
.pagination-container {    
    display: flex;    
    justify-content: flex-start;  /*将子元素对齐到容器的开头，也可以用left，默认left */    
    /* justify-content: center;  /*将子元素对齐到容器的中间 */ 
    /*justify-content: right;  /*将子元素对齐到容器的右边 */  
    align-items: center; /* 垂直居中 */    
}    
    
.total-records {    
    margin-left: 50px;  
    /* font-size: 16px;  等于根元素字体大小，通常为16px */
    color:green       
}    
</style>