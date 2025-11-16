
import SvgIcon from './SvgIcon/index.vue'
import SvgInput from './SvgIcon/iconInput.vue'
import AnimatedLoading from './AnimatedLoading.vue';

const allGloablCom = {
  SvgIcon,
  SvgInput,
  AnimatedLoading
}


export default {
  install(app) {
    Object.keys(allGloablCom).forEach((key) => {
      app.component(key, allGloablCom[key])
    })
  }
}