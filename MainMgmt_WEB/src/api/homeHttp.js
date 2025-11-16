import http from "./http"

// 获取当日告警数量
const alarmToday = () => {
  const path = "/api/alert/statistic";
  return http.get(path);
}

// 获取当日告警数量
const celeryToday = () => {
  const path = "/api/home/log-stats";
  return http.get(path);
}


// 获取布局
const getLayout = () =>{
  const path ="/api/home/layout"
  return http.get(path)
}

const updateLayout = (id,data) => {
  const path = "/api/home/layout/" + id;
  return http.put(path,data);
}

export default{
     alarmToday,
    celeryToday,
    getLayout,
    updateLayout
}