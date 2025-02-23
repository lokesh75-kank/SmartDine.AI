import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  base: 'SmartDine.AI',  // Sets the base URL path
  plugins: [react()],
})
