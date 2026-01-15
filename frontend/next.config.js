/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
  },
  // Отключаем статическую оптимизацию для всех страниц
  experimental: {
    isrMemoryCacheSize: 0,
  },
}

module.exports = nextConfig
