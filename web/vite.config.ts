import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vitest/config'
import path from 'path'
import { fileURLToPath } from 'url'

export default defineConfig({
  base: '/UPAY-Optimized/',
  plugins: [react(), tailwindcss()],
  server: {
    proxy: { '/api': 'http://localhost:8000' },
    watch: {
      ignored: [
        '**/node_modules/**',
        '**/dist/**',
        '**/.git/**',
      ],
      usePolling: false,
    },
    hmr: {
      timeout: 5000,
    },
  },
  optimizeDeps: {
    entries: ['src/**/*.{ts,tsx}'],
  },
  test: {
    environment: 'node',
    include: ['src/**/*.test.ts'],
  },
})
