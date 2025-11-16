// 将日期对象或日期字符串转换为格式化的字符串 "YYYY-MM-DD"
const stringFromDate = (date) => {
    if (!date) {
        return '';  // 没有数据返回空
    }
    if (typeof date === 'string') {
        date = new Date(date);
    }

    // 从 Date 对象中提取年份
    const year = date.getFullYear();
    const month = (date.getMonth() + 1).toString().padStart(2, '0');

    // 从 Date 对象中提取日期
    // 将日期转换为字符串，并使用 padStart 确保两位数，不足两位时在前面补零
    const day = date.getDate().toString().padStart(2, '0');

    // 构造格式化的日期字符串，格式为 "YYYY-MM-DD"
    const formattedDate = `${year}-${month}-${day}`;
    return formattedDate;
};

// 日期对象或日期字符串转换为格式化的字符串 "YYYY-MM-DD HH:MM:SS"
const stringFromDateTime = (date) => {
    if (!date) {
        return '';  // 没有数据返回空
    }
    if (typeof date === 'string') {
        date = new Date(date);
    }

    // 从 Date 对象中提取年份
    const year = date.getFullYear();

    // 从 Date 对象中提取月份并加1（JavaScript 中的月份是从0开始的）
    const month = (date.getMonth() + 1).toString().padStart(2, '0');

    // 从 Date 对象中提取日期
    const day = date.getDate().toString().padStart(2, '0');

    // 从 Date 对象中提取小时
    const hour = date.getHours().toString().padStart(2, '0');

    // 从 Date 对象中提取分钟
    const minute = date.getMinutes().toString().padStart(2, '0');

    // 从 Date 对象中提取秒数
    const second = date.getSeconds().toString().padStart(2, '0');

    // 构造格式化的日期时间字符串，格式为 "YYYY-MM-DD HH:MM:SS"
    const formattedDate = `${year}-${month}-${day} ${hour}:${minute}:${second}`;

    return formattedDate;
};

// 导出默认对象，其中包含 stringFromDate 和 stringFromDateTime 函数
export default {
    stringFromDate: stringFromDate,
    stringFromDateTime
};
