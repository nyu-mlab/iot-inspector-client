import { defineConfig } from 'vite'
const { resolve, join } = require('path')
import react from '@vitejs/plugin-react'
import ViteFonts from 'vite-plugin-fonts'


// https://vitejs.dev/config/
export default defineConfig({
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@components': resolve(__dirname, 'src/components'),
      '@hooks': resolve(__dirname, 'src/hooks'),
      '@utils': resolve(__dirname, 'src/utils'),
      '@contexts': resolve(__dirname, 'src/contexts'),
    }
  },
  build: {
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
        // nested: resolve(__dirname, 'getting-started/index.html')
        // main: join(__dirname, '../../', 'html', 'index.html')
        // main: resolve(__dirname, '..', 'html/index.html')
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
      '/graphql': {
        target: 'http://127.0.0.1:4000',
        changeOrigin: true,
        secure: false,
        ws: true,
      }
    }
  },
  // base: '/dashboard/html/',
  // build: {
  //   // assetsDir: '/dashboard/html/',
  //   outDir: '../html',
  //   emptyOutDir: true
  // }
})

