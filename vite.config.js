import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  base: './',
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    open: false,
  },
  build: {
    chunkSizeWarningLimit: 850,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            return 'vendor'
          }
          if (id.includes('data/knowledge.json') || id.includes('data\\knowledge.json')) {
            return 'data-knowledge'
          }
          if (id.includes('src/modules/solve') || id.includes('src\\modules\\solve')) {
            return 'module-solve'
          }
        }
      }
    }
  }
})
