/* 获取缩放比例全屏
 * @param {boolean} containRatio 是否计算设备像素比
 * @param {number | string} baseWidth 基础宽度
 */
const getScale = (containRatio = true, baseWidth = 1920) => {
  const currentScale = document.documentElement.clientWidth / baseWidth
  const formattedScale = currentScale > 1 ? currentScale : 1
  const resultScale = containRatio ? formattedScale * window.devicePixelRatio : formattedScale
  return Math.ceil(resultScale)
}



export default {
  getScale
}