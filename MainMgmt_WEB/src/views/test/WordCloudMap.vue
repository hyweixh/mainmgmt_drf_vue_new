<script setup>
import * as echarts from "echarts";
import "echarts-wordcloud";
import { onMounted } from "vue";
import VueData from './vue.json'

// 初始化词云图
function initCharts() {
  // 获取容器并初始化图表
  const chart = echarts.init(document.getElementById('container'));



    // 创建一个 Image 对象并加载本地图片
    var maskImage = new Image();
    maskImage.src = 'data:image/png;base64,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'

  // 设置图表配置项
  chart.setOption({
    title: {
      text: '',
      link: 'http://www.google.com/trends/hottrends'  // 标题点击链接
    },
    tooltip: {
      show: true  // 显示提示框
    },
    grid: {
      left: '0%',  // 左边距
      right: '0%', // 右边距
      bottom: '0%', // 下边距
      top: '0%',   // 上边距
      containLabel: true // 包含标签
    },
    series: [{
      type: 'wordCloud',  // 词云图类型
      maskImage: maskImage,
      gridSize: 16,        // 控制词云图的网格大小
      sizeRange: [22, 60], // 控制词语的大小范围
      rotationRange: [0, 0], // 词语的旋转角度范围
      rotationStep: 20,    // 控制词语旋转的步长
      shape: 'circle',     // 词云图的形状（支持 circle, cardioid, diamond, 等）
      drawOutOfBound: false, // 不允许词语超出绘制区域
      layoutAnimation: true, // 开启布局动画
      left: 'center',      // 图表水平居中
      top: 'center',       // 图表垂直居中
      textStyle: {
        fontFamily: 'Verdana',  // 设置字体
        color: getRandomColor
      },
      data: VueData,  // 绑定词汇数据
      emphasis: {
        // focus: 'self',  // 点击词汇时高亮
        // textStyle: {
        //   fontSize: 58  // 被点击的词语放大
        // }
      }
    }]
  });

}

function getRandomColor() {
  const arr = [
    '#5B8FF9',
    '#5AD8A6',
    '#5D7092',
    '#F6BD16',
    '#E8684A',
    '#6DC8EC',
    '#9270CA',
    '#FF9D4D',
    '#269A99',
    '#FF99C3',
  ];
  return arr[Math.floor(Math.random() * (arr.length - 1))];
}

// Vue 生命周期钩子：组件挂载后执行
onMounted(() => {
  initCharts();  // 初始化词云图
});
</script>


<template>

  <div id="container" style="height: 1000px; width: 1300px;display: flex;"></div>


    


</template>

<style scoped>
</style> 