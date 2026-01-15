'use client'

import { useState, useEffect } from 'react'
import { apiClient } from '../lib/api'

interface MainScreenProps {
  initData: string
}

export default function MainScreen({ initData }: MainScreenProps) {
  const [clone, setClone] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadClone()
  }, [])

  const loadClone = async () => {
    try {
      const cloneData = await apiClient.getClone(initData)
      setClone(cloneData)
    } catch (error: any) {
      if (error.response?.status === 404) {
        // Клон еще не создан
        setClone(null)
      } else {
        console.error('Error loading clone:', error)
      }
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Загрузка...</p>
        </div>
      </div>
    )
  }

  if (!clone) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white p-4">
        <div className="max-w-md mx-auto mt-8 text-center">
          <h1 className="text-3xl font-bold mb-4">Создай своего клона</h1>
          <p className="text-gray-600 mb-8">
            Запиши свой первый дневник, чтобы создать ИИ-клона
          </p>
          <button
            onClick={() => window.location.href = '/diary'}
            className="bg-blue-500 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-600 transition"
          >
            Записать дневник
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-md mx-auto">
        <div className="bg-white rounded-lg shadow-md p-6 mb-4">
          <h1 className="text-2xl font-bold mb-4">Твой клон</h1>
          
          <div className="mb-4">
            <div className="flex justify-between items-center mb-2">
              <span className="text-gray-600">Точность клона</span>
              <span className="font-bold">{clone.accuracy_score}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-500 h-2 rounded-full"
                style={{ width: `${clone.accuracy_score}%` }}
              ></div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4 mb-4">
            <div className="bg-blue-50 p-3 rounded-lg">
              <div className="text-2xl font-bold">{clone.diaries_count}</div>
              <div className="text-sm text-gray-600">Дневников</div>
            </div>
            <div className="bg-green-50 p-3 rounded-lg">
              <div className="text-2xl font-bold">{clone.status === 'active' ? '✓' : '...'}</div>
              <div className="text-sm text-gray-600">Статус</div>
            </div>
          </div>

          <div className="space-y-2">
            <button
              onClick={() => window.location.href = '/diary'}
              className="w-full bg-blue-500 text-white py-3 rounded-lg font-semibold hover:bg-blue-600 transition"
            >
              Записать дневник
            </button>
            <button
              onClick={() => window.location.href = '/ask'}
              className="w-full bg-gray-200 text-gray-800 py-3 rounded-lg font-semibold hover:bg-gray-300 transition"
            >
              Спросить у клона
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
