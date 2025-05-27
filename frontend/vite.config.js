// frontend/vite.config.js
import { defineConfig } from 'vite'

// Если ты используешь какой-то фреймворк, типа Vue или React,
// то тут может быть соответствующий плагин, например:
// import vue from '@vitejs/plugin-vue'

export default defineConfig({
  // plugins: [vue()], // Раскомментируй, если используешь Vue, например
  server: {
    port: 5173, // Можешь указать порт явно, если хочешь
    proxy: {
      // Проксируем все запросы, начинающиеся с /api, на твой Flask-сервер
      '/api': {
        target: 'http://localhost:5000', // Адрес твоего Flask-сервера
        changeOrigin: true, // Необходимо для виртуальных хостов
        // secure: false, // Если у Flask самоподписанный SSL-сертификат (обычно не нужно для http)
        // rewrite: (path) => path.replace(/^\/api/, '') // Раскомментируй, если Flask не ожидает /api в URL
                                                        // Например, если Flask роут /auth/login, а ты с фронта шлешь /api/auth/login,
                                                        // то rewrite сделает из этого /auth/login для Flask.
                                                        // В твоем случае Flask ожидает /api/*, так что rewrite НЕ НУЖЕН.
      }
    }
  }
})