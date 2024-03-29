import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000 // 修改為想要的端口號
  },
  output: [
    {
      file: 'rsuite/DateRangePicker/styles/index.css',
      format: 'map',
      sourcemap: true,
    }
  ]
})
