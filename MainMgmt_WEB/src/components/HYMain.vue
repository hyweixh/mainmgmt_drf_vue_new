<script setup>
    import HYPageHeader from "@/components/HYPageHeader.vue"

   // import { defineProps } from "vue"

    let props = defineProps({
        // title: ""
    })

</script>

<template>
    <!-- fill :size="5" el-card之间的距离-->
    <el-space direction="vertical" fill :size="5" style="width: 100%">
        <HYPageHeader :content="props.title"></HYPageHeader>
        <!-- 预留插槽 -->
        <slot></slot>
    </el-space>
</template>

<style scoped>
    .el-space :deep(.el-space__item) {
        width: 100%;
    }
</style>