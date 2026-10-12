import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:4000',
      '/demo-videos': 'http://127.0.0.1:4000',
    },
    fs: {
      allow: ['.', path.resolve(__dirname, 'test_videos')],
    },
  },
})
