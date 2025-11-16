<template>
    <div class="server-container">
      <!-- 页面标题 -->
      <div class="page-title">这是服务器管理页面</div>
      
      <!-- 配置步骤说明 -->
      <div class="config-steps">
        <p class="step-item">1. 在 view/auth/ 目录下添加 server.vue 文件</p>
        <p class="step-item">2. 在 /views/route/frame.js 中导入 server.vue：</p>
        <p class="code-line">import server from '@/views/auth/server.vue';</p>
        <p class="step-item">3. 在路由（routes）的 children 数组中添加：</p>
        <pre class="code-block">
            children: [
                {
                path: 'server',
                name: 'server',
                component: server,
                },
         ]</pre>
      </div>
    </div>
  </template>
  
  <style scoped>
  /* 容器统一样式，避免内容贴边 */
  .server-container {
    padding: 20px;
  }
  
  /* 页面标题：较大字体，突出显示 */
  .page-title {
    font-size: 24px; /* 比默认30px更适中，避免过大 */
    font-weight: bold;
    margin-bottom: 20px;
    color: #333;
  }
  
  /* 步骤说明文本：常规阅读字体 */
  .config-steps {
    font-size: 16px; /* 步骤文字清晰易读 */
    color: #666;
    line-height: 1.8; /* 行高增加，提升阅读体验 */
  }
  
  /* 步骤序号文本：轻微加粗，区分步骤 */
  .step-item {
    margin: 10px 0;
    font-weight: 500;
  }
  
  /* 单行代码：等宽字体，突出代码 */
  .code-line {
    font-size: 14px;
    font-family: "Consolas", "Monaco", monospace; /* 代码专用字体 */
    color: #0066cc;
    background-color: #f5f7fa;
    padding: 4px 8px;
    border-radius: 4px;
    display: inline-block;
    margin: 5px 0;
  }
  
  /* 代码块：独立区域，清晰展示 */
  .code-block {
    font-size: 14px;
    font-family: "Consolas", "Monaco", monospace;
    color: #333;
    background-color: #f5f7fa;
    padding: 12px;
    border-radius: 4px;
    border-left: 3px solid #0066cc;
    margin: 10px 0;
    overflow-x: auto; /* 代码过长时可横向滚动 */
  }
  </style>