<script setup>
    import '@/assets/css/light.css'
    import '@/assets/css/elementPlus.css'
    import '@/assets/css/global-scrollbar.css'
</script>

<template>
  <router-view />
</template>

<style>
    .el-input__inner,
    .el-textarea__inner,
    .el-select .el-input__inner,
    .el-button,
    .el-form-item {
      font-family: var(--my-font-family) !important;
    }

    :root {
      --el-color-primary: #626aef;
      --el-color-primary-light-3: #f56c6c;
      --dark-background-color:#151617;
      --dark-background-card:#1D1E1F;
      --light-background-card:#FFFFFF;
      --dark-text-blod:#CFD3DC;
      --el-color-primary-light-9:#eff0fd;
      --el-text-color-secondary:#525a6e;
      --dark-underline:#323232;
      --light-underline:#e6e6e6;
      --light-background-gm:#f4f6f9;

      --el-color-warning: #fac858;
      --el-color-green: #4fc08d;
      --el-color-red: #f56c6c;
      --el-color-unknown: #767a72;
    }

    #nprogress .bar {
      background: var(--el-color-primary) !important;
    }
    #nprogress .peg {
      box-shadow: 0 0 10px rgb(98, 106, 239), 0 0 5px rgb(98, 106, 239) !important;
    }

    .drawer-header-container {
      padding-bottom: 10px;
      display: flex;
      justify-content: space-between;
    }

    button:focus, .el-button:focus {
      outline: none;
      box-shadow: none;
    }

    .status-dot {
      display: inline-block;
      width: 10px;
      height: 10px;
      border-radius: 100%;
      margin-right: 5px;
    }

    .icon-green { color: var(--el-color-green); }
    .icon-red { color: #f56c6c; }

    .status-normal { background-color: var(--el-color-green); }
    .status-error { background-color: #f56c6c; }
    .status-warning { background-color: #fac858; }
    .status-unknown { background-color: #767a72; }

    .location-container { display: flex; align-items: center; }
    .table-container { padding: 10px; border-radius: 8px; }
    .table-link{ font-size: 12px; }
    .cmdb_table { width: 100%; height: 72vh; font-size: 12px; }

    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }

    .update-button-dq { display: inline-flex; align-items: flex-end; }
    .upload-demo { margin-left: 10px; }

    .layout-card,.layout-card-fixed {
      border-radius: 4px;
      overflow: hidden;
      box-sizing: border-box;
    }

    .button-container { display: flex; align-items: center; margin-bottom: 2px; }
    .operation-mini-icon { height: 100%; border: none; transition: transform 0.3s ease; }

    .center-flex { display: flex; align-items: center; justify-content: center; gap: 4px; }
    .left-flex { display: flex; align-items: center; gap: 4px; }

    .el-table .cell {
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .space_4px{ margin-left: 0px; margin-right: 4px; }
</style>