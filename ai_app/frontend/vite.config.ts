import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"
import pluginRewriteAll from "vite-plugin-rewrite-all"

export default defineConfig({
  plugins: [react(), pluginRewriteAll()],
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
})
