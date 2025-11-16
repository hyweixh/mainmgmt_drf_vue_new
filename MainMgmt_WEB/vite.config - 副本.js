import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import VueSetupExtend from 'vite-plugin-vue-setup-extend'

import path from 'path' //内置模块，处理和解析文件路径
import { createSvgIconsPlugin } from 'vite-plugin-svg-icons' //处理 SVG 图标的自动导入
import Components from 'unplugin-vue-components/vite';
import { AntDesignVueResolver } from 'unplugin-vue-components/resolvers'; //ant

const dirPath = path.dirname(fileURLToPath(import.meta.url)) //获取当前文件的路径

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    createSvgIconsPlugin({
      // 指定需要缓存的图标文件夹
      iconDirs: [
        // 这里分为了一般icon文件夹和文件图标类型文件夹，方便管理，可以按照需求设置更多分类
        path.resolve(dirPath, 'src/assets/icons')
      ],
      // 指定symbolId格式
      symbolId: 'icon-[dir]-[name]'
    }),
    Components({
      resolvers: [
        AntDesignVueResolver({
          importStyle: false, // css in js
        }),
      ],
    }),
    vue(),
    VueSetupExtend()
  ],
  base: './', // 确保资源文件以相对路径加载
  build: {
    assetsDir: 'assets', // 设置打包后的静态资源目录
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    host: '0.0.0.0',  // 监听所有地址，允许用局域网IP访问
    port: 5173        // 可保持默认端口，也可修改
  }
})
