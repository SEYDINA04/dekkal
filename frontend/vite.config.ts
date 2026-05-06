import path from "path";
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

const backendUrl = process.env.BACKEND_URL || "http://localhost:8001";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src")
    }
  },
  server: {
    port: 5174,
    strictPort: false,
    host: true,
    allowedHosts: true,
    proxy: {
      "/api": { target: backendUrl, changeOrigin: true },
      "/docs": { target: backendUrl, changeOrigin: true },
      "/redoc": { target: backendUrl, changeOrigin: true },
      "/openapi.json": { target: backendUrl, changeOrigin: true },
    }
  }
});
