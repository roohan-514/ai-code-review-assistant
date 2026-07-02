import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE,
  timeout: 120000,
  headers: { 'Content-Type': 'application/json' },
})

export async function checkHealth() {
  const { data } = await api.get('/health')
  return data
}

export async function getLanguages() {
  const { data } = await api.get('/languages')
  return data.languages
}

export async function reviewCode(code, language, fileName = null) {
  const payload = { code, language }
  if (fileName) payload.file_name = fileName
  const { data } = await api.post('/review-code', payload)
  return data
}

export async function reviewPR(prUrl) {
  const { data } = await api.post('/review-pr', { pr_url: prUrl })
  return data
}

export default api
