import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const apiClient = {
  // Onboarding
  async getOnboardingStatus(initData: string) {
    const response = await api.get('/onboarding/status', {
      headers: { 'X-Telegram-Init-Data': initData },
    })
    return response.data
  },

  async saveOnboardingAnswer(initData: string, field: string, value: string) {
    const response = await api.post(
      '/onboarding/answer',
      { field, value },
      { headers: { 'X-Telegram-Init-Data': initData } }
    )
    return response.data
  },

  async guessGender(initData: string, name: string) {
    const response = await api.get('/onboarding/guess-gender', {
      params: { name },
      headers: { 'X-Telegram-Init-Data': initData },
    })
    return response.data
  },

  // Diaries
  async createDiaryText(initData: string, text: string) {
    const response = await api.post(
      '/diaries',
      { text },
      { headers: { 'X-Telegram-Init-Data': initData } }
    )
    return response.data
  },

  async createDiaryAudio(initData: string, audioFile: File) {
    const formData = new FormData()
    formData.append('audio', audioFile)
    
    const response = await api.post('/diaries', formData, {
      headers: {
        'X-Telegram-Init-Data': initData,
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  async getDiaries(initData: string) {
    const response = await api.get('/diaries', {
      headers: { 'X-Telegram-Init-Data': initData },
    })
    return response.data
  },

  // Clone
  async getClone(initData: string) {
    const response = await api.get('/clone', {
      headers: { 'X-Telegram-Init-Data': initData },
    })
    return response.data
  },

  async askClone(initData: string, question: string) {
    const response = await api.post(
      '/clone/ask',
      { question },
      { headers: { 'X-Telegram-Init-Data': initData } }
    )
    return response.data
  },

  // Profile
  async getProfile(initData: string) {
    const response = await api.get('/profile', {
      headers: { 'X-Telegram-Init-Data': initData },
    })
    return response.data
  },
}
