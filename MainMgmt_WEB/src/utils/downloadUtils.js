// utils/downloadUtils.js

import { ElMessage } from 'element-plus';

export const downloadFile = (data, filename, type, withTimestamp = true) => {
    const blob = new Blob([data], { type: type });
    const url = window.URL.createObjectURL(blob);

    // 生成时间戳
    let finalName = filename;
    if (withTimestamp) {
        const timestamp = new Date().toISOString().replace(/[-:T]/g, '').split('.')[0];
        // 处理文件后缀
        const dotIndex = filename.lastIndexOf('.');
        if (dotIndex !== -1) {
            const name = filename.substring(0, dotIndex);
            const ext = filename.substring(dotIndex);
            finalName = `${name}_${timestamp}${ext}`;
        } else {
            finalName = `${filename}_${timestamp}`;
        }
    }

    // 创建一个隐藏的 <a> 标签，用于触发下载
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', finalName);
    document.body.appendChild(link);
    link.click();

    // 下载完成后清理
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);

    ElMessage.success(`文件 ${finalName} 下载成功`);
};
