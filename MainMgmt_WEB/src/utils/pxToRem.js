// utils/pxToRem.js

/**
 * 将 px 转换为 rem
 * @param {string} style - 要转换的 CSS 样式（内联样式）
 * @param {number} designWidth - 设计稿宽度（默认为1920）
 * @param {number} rootValue - 基准值（默认为192）
 * @returns {string} 转换后的 rem 样式
 */
const pxToRem = (style, designWidth = 1920, rootValue = 192) => {
  const remBase = rootValue / designWidth;  // 计算 rem 单位与 px 单位的转换比例

  // 转换样式中的 px 为 rem
  return style.replace(/(\d*\.?\d+)px/g, (match, p1) => {
    const pxValue = parseFloat(p1);
    const remValue = pxValue * remBase;  // 计算 rem 值
    return `${remValue}rem`;  // 返回转换后的 rem 单位
  });
}

export default pxToRem;
