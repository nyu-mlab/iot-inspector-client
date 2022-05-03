import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [ react() ],
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:53721',
        changeOrigin: true,
        secure: false,
        ws: true,
      }
    }
  },
  // devServer: {
  //   proxy: "http://127.0.0.1:53721"
  // }
})
