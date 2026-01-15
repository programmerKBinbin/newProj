import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Clone Platform',
  description: 'Платформа ИИ-клонов',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ru">
      <body>{children}</body>
    </html>
  )
}
