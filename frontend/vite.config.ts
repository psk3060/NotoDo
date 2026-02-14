import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'
import path from "path";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // @ Alias 설정
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  // Vite + Sass에서 Bootstrap 사용 시 경고 제거
  css: {
    preprocessorOptions: {
      scss: {
        quietDeps: true,
      },
    },
  }
})
