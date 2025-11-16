
/*
根据传入的主题给对应的echarts颜色
*/ 

const getEchartsTextColor = (theme) => theme === 'dark' ? '#CFD3DC' : '#606266';  //文字颜色
const getEchartsbkgColor = (theme) => theme === 'dark' ? '#1D1E1F' : '#fff';    //背景色
const getUnderlineColor = (theme) => theme === 'dark' ? '#323232' : '#E0E6F1';  //虚线

  

export default{
  getEchartsTextColor,
  getEchartsbkgColor,
  getUnderlineColor
}