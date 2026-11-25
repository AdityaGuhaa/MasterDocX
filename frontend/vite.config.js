// Copyright (c) 2026 Aditya Guha
// SPDX-License-Identifier: MIT

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Document IDs are file names (e.g. /viewer/report.pdf). Vite's SPA fallback
// skips URLs that look like files, so reloading a viewer page would 404.
// Serve the app for every /viewer/* URL instead.
const rewriteViewer = (req, _res, next) => {
  if (req.url && req.url.startsWith('/viewer/')) {
    req.url = '/index.html'
  }
  next()
}

const viewerFallback = () => ({
  name: 'viewer-fallback',
  configureServer(server) {
    server.middlewares.use(rewriteViewer)
  },
  configurePreviewServer(server) {
    server.middlewares.use(rewriteViewer)
  },
})

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react(), viewerFallback()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      }
    }
  }
})
