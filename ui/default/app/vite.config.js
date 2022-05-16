import { defineConfig } from 'vite'
const { resolve } = require('path')
import react from '@vitejs/plugin-react'
import ViteFonts from 'vite-plugin-fonts'


// https://vitejs.dev/config/
export default defineConfig({
  build: {
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
        nested: resolve(__dirname, 'getting-started/index.html')
      }
    }
  },
  plugins: [
    react(),
    ViteFonts({
      google: {
        families: ['Open Sans',
        {
          name: 'Open Sans',
          styles: 'wght@400,500,600,700'
        }
      ],
      },
    }),
   ],
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
