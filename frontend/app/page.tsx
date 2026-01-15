'use client'

import { useEffect, useState } from 'react'
import Onboarding from './components/Onboarding'
import MainScreen from './components/MainScreen'
import { apiClient } from './lib/api'

// Указываем Next.js, что страница должна рендериться динамически
export const dynamic = 'force-dynamic'

export default function Home() {
  const [initData, setInitData] = useState<string | null>(null)
  const [onboardingCompleted, setOnboardingCompleted] = useState<boolean | null>(null)
  const [loading, setLoading] = useState(true)
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
    
    // Работаем только на клиенте
    if (typeof window === 'undefined') {
      return
    }
    
    // Получаем Telegram Web App объект
    const tg = (window as any).Telegram?.WebApp
    
    if (!tg) {
      setLoading(false)
      return
    }
    
    // Инициализация Telegram Web App (если доступно)
    if (tg.ready) {
      tg.ready()
    }
    
    // Получаем initData
    let dataString: string | null = null
    
    if (tg.initData) {
      // Если есть готовый initData
      dataString = tg.initData
    } else if (tg.initDataUnsafe) {
      // Формируем initData из объекта initDataUnsafe
      const params = new URLSearchParams()
      const unsafe = tg.initDataUnsafe
      
      if (unsafe.user) {
        params.append('user', JSON.stringify(unsafe.user))
      }
      if (unsafe.auth_date) {
        params.append('auth_date', unsafe.auth_date.toString())
      }
      if (unsafe.hash) {
        params.append('hash', unsafe.hash)
      }
      if (unsafe.query_id) {
        params.append('query_id', unsafe.query_id)
      }
      
      dataString = params.toString()
    }
    
    if (dataString) {
      setInitData(dataString)
      checkOnboardingStatus(dataString)
    } else {
      // Для тестирования вне Telegram можно использовать тестовые данные
      console.warn('Telegram Web App data not found. Running in test mode.')
      setLoading(false)
    }
  }, [])

  const checkOnboardingStatus = async (data: string) => {
    try {
      const status = await apiClient.getOnboardingStatus(data)
      setOnboardingCompleted(status.completed)
    } catch (error) {
      console.error('Error checking onboarding status:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleOnboardingComplete = () => {
    setOnboardingCompleted(true)
  }

  if (!mounted || loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Загрузка...</p>
        </div>
      </div>
    )
  }

  if (!initData) {
    return (
      <div className="flex items-center justify-center min-h-screen p-4">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Ошибка</h1>
          <p className="text-gray-600 mb-4">Не удалось получить данные от Telegram</p>
          <p className="text-sm text-gray-500">
            Убедитесь, что вы открыли приложение через Telegram бота
          </p>
        </div>
      </div>
    )
  }

  if (onboardingCompleted === false) {
    return <Onboarding initData={initData} onComplete={handleOnboardingComplete} />
  }

  return <MainScreen initData={initData} />
}
