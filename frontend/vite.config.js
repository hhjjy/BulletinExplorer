import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'
import envCompatible from 'vite-plugin-env-compatible';
import { resolve } from 'path';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react(), envCompatible(),],
  server: {
    port: 3000 // 修改為想要的端口號
  },
  output: [
    {
      file: 'rsuite/DateRangePicker/styles/index.css',
      format: 'map',
      sourcemap: true,
    }
  ],
  resolve: {
    alias: {
      '@': resolve(__dirname, './src') // 設置別名以便引用
    },
  }
})
