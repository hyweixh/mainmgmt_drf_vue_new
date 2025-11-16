import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import VueSetupExtend from 'vite-plugin-vue-setup-extend'

import path from 'path' 
import { createSvgIconsPlugin } from 'vite-plugin-svg-icons'
import Components from 'unplugin-vue-components/vite';
import { AntDesignVueResolver } from 'unplugin-vue-components/resolvers';

const dirPath = path.dirname(fileURLToPath(import.meta.url))

export default defineConfig({
  plugins: [
    createSvgIconsPlugin({
      iconDirs: [
        path.resolve(dirPath, 'src/assets/icons')
      ],
      symbolId: 'icon-[dir]-[name]'
    }),
    Components({
      resolvers: [
        AntDesignVueResolver({
          importStyle: false,
        }),
      ],
    }),
    vue(),
    VueSetupExtend()
  ],
  base: './',
  build: {
    assetsDir: 'assets',
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    // ✅ 添加这行配置：代理API请求到后端
    proxy: {
      '/api': {
        target: 'http://localhost:8000',  // 你的Django后端地址
        changeOrigin: true,
        secure: false,
      }
    }
  }
})