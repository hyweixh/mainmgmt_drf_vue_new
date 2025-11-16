<template>
    <div class="order-page">
      <!-- 页面标题 -->
      <div class="page-title">这是服务器管理页面</div>
  
      <!-- 配置步骤说明区 -->
      <div class="config-guide">
        <p class="guide-step">1. 在 view/auth/ 目录下添加 order 相关文件（如 order.vue）</p>
        
        <p class="guide-step">2. 在 /views/route/frame.js 中导入 order.vue：</p>
        <!-- 单行代码 -->
        <div class="code-single">import order from '@/views/auth/order.vue';</div>
        
        <p class="guide-step">3. 在路由（routes）的 children 数组中添加：</p>
        <!-- 代码块 -->
        <div class="code-block">
            children: [
                {
                    path: '/order',
                    name: 'order',
                    component: order,
                },
            ]
        </div>
      </div>
    </div>
  </template>
  
  <style scoped>
  /* 页面容器：控制整体间距 */
  .order-page {
    padding: 20px;
  }
  
  /* 页面标题：突出且不刺眼 */
  .page-title {
    font-size: 24px; /* 比原30px更协调，适合标题 */
    font-weight: bold;
    color: #2c3e50;
    margin-bottom: 25px;
  }
  
  /* 步骤说明文本：常规阅读舒适尺寸 */
  .config-guide {
    font-size: 16px; /* 步骤文字清晰，避免过小 */
    color: #34495e;
    line-height: 2; /* 行高拉开，减少拥挤感 */
  }
  
  /* 单个步骤：增加上下间距 */
  .guide-step {
    margin: 12px 0;
  }
  
  /* 单行代码：等宽字体，区分普通文本 */
  .code-single {
    font-size: 14px;
    font-family: "Consolas", "Monaco", monospace; /* 代码专用字体，字符更规整 */
    color: #27ae60;
    background: #f8f9fa;
    padding: 6px 12px;
    border-radius: 4px;
    margin: 8px 0;
    display: inline-block;
  }
  
  /* 代码块：独立区域，便于查看多行代码 */
  .code-block {
    font-size: 14px;
    font-family: "Consolas", "Monaco", monospace;
    color: #2c3e50;
    background: #f8f9fa;
    padding: 15px;
    border-radius: 4px;
    border-left: 3px solid #27ae60;
    margin: 8px 0;
    overflow-x: auto; /* 代码过长时可横向滚动，避免换行混乱 */
  }
  </style>