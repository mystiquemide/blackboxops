import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    watch: {
      ignored: ['**/.venv/**', '**/venv/**', '**/__pycache__/**', '**/node_modules/**', '**/dist/**'],
    },
    proxy: {
      '/api': {
        target: process.env.BLACKBOXOPS_API_URL ?? 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
