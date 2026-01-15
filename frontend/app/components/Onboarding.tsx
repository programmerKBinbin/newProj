'use client'

import { useState, useEffect } from 'react'
import { apiClient } from '../lib/api'

interface OnboardingProps {
  initData: string
  onComplete: () => void
}

type Step = 'welcome' | 'name' | 'age' | 'city' | 'gender' | 'complete'

export default function Onboarding({ initData, onComplete }: OnboardingProps) {
  const [step, setStep] = useState<Step>('welcome')
  const [name, setName] = useState('')
  const [age, setAge] = useState('')
  const [city, setCity] = useState('')
  const [gender, setGender] = useState('')
  const [genderGuess, setGenderGuess] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (step === 'gender' && name) {
      apiClient.guessGender(initData, name).then((data) => {
        setGenderGuess(data.gender)
      })
    }
  }, [step, name, initData])

  const handleNext = async () => {
    setLoading(true)
    try {
      if (step === 'welcome') {
        setStep('name')
      } else if (step === 'name') {
        await apiClient.saveOnboardingAnswer(initData, 'name', name)
        setStep('age')
      } else if (step === 'age') {
        await apiClient.saveOnboardingAnswer(initData, 'age', age)
        setStep('city')
      } else if (step === 'city') {
        await apiClient.saveOnboardingAnswer(initData, 'city', city)
        setStep('gender')
      } else if (step === 'gender') {
        await apiClient.saveOnboardingAnswer(initData, 'gender', gender)
        setStep('complete')
        setTimeout(() => onComplete(), 1000)
      }
    } catch (error) {
      console.error('Error saving answer:', error)
      alert('Ошибка при сохранении. Попробуйте еще раз.')
    } finally {
      setLoading(false)
    }
  }

  const canProceed = () => {
    if (step === 'welcome') return true
    if (step === 'name') return name.length >= 2
    if (step === 'age') return age && parseInt(age) >= 13 && parseInt(age) <= 120
    if (step === 'city') return city.length >= 2
    if (step === 'gender') return gender !== ''
    return false
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white p-4">
      <div className="max-w-md mx-auto mt-8">
        {step === 'welcome' && (
          <div className="text-center">
            <h1 className="text-3xl font-bold mb-4">Добро пожаловать! 👋</h1>
            <p className="text-gray-600 mb-8">
              Я помогу создать твоего ИИ-клона. Давай начнем с нескольких вопросов.
            </p>
            <button
              onClick={handleNext}
              className="bg-blue-500 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-600 transition"
            >
              Начать
            </button>
          </div>
        )}

        {step === 'name' && (
          <div>
            <h2 className="text-2xl font-bold mb-4">Как тебя зовут?</h2>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Введите ваше имя"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg mb-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={handleNext}
              disabled={!canProceed() || loading}
              className="w-full bg-blue-500 text-white py-3 rounded-lg font-semibold hover:bg-blue-600 transition disabled:opacity-50"
            >
              {loading ? 'Сохранение...' : 'Далее'}
            </button>
          </div>
        )}

        {step === 'age' && (
          <div>
            <h2 className="text-2xl font-bold mb-4">Сколько тебе лет?</h2>
            <input
              type="number"
              value={age}
              onChange={(e) => setAge(e.target.value)}
              placeholder="Введите ваш возраст"
              min="13"
              max="120"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg mb-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={handleNext}
              disabled={!canProceed() || loading}
              className="w-full bg-blue-500 text-white py-3 rounded-lg font-semibold hover:bg-blue-600 transition disabled:opacity-50"
            >
              {loading ? 'Сохранение...' : 'Далее'}
            </button>
          </div>
        )}

        {step === 'city' && (
          <div>
            <h2 className="text-2xl font-bold mb-4">Из какого ты города?</h2>
            <input
              type="text"
              value={city}
              onChange={(e) => setCity(e.target.value)}
              placeholder="Введите название города"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg mb-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={handleNext}
              disabled={!canProceed() || loading}
              className="w-full bg-blue-500 text-white py-3 rounded-lg font-semibold hover:bg-blue-600 transition disabled:opacity-50"
            >
              {loading ? 'Сохранение...' : 'Далее'}
            </button>
          </div>
        )}

        {step === 'gender' && (
          <div>
            <h2 className="text-2xl font-bold mb-4">
              {genderGuess && genderGuess !== 'unknown' 
                ? `Вы ${genderGuess === 'male' ? 'мужчина' : 'женщина'}?`
                : 'Вы мужчина или женщина?'}
            </h2>
            <div className="space-y-2 mb-4">
              {['male', 'female', 'other'].map((g) => (
                <button
                  key={g}
                  onClick={() => setGender(g)}
                  className={`w-full py-3 rounded-lg border-2 transition ${
                    gender === g
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-300 hover:border-gray-400'
                  }`}
                >
                  {g === 'male' ? 'Мужчина' : g === 'female' ? 'Женщина' : 'Другое'}
                </button>
              ))}
            </div>
            <button
              onClick={handleNext}
              disabled={!canProceed() || loading}
              className="w-full bg-blue-500 text-white py-3 rounded-lg font-semibold hover:bg-blue-600 transition disabled:opacity-50"
            >
              {loading ? 'Сохранение...' : 'Завершить'}
            </button>
          </div>
        )}

        {step === 'complete' && (
          <div className="text-center">
            <div className="text-6xl mb-4">✅</div>
            <h2 className="text-2xl font-bold mb-4">Отлично!</h2>
            <p className="text-gray-600">
              Теперь давай создадим твоего клона. Запиши свой первый дневник!
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
