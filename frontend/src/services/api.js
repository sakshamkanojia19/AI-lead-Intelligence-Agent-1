import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
})

export const researchLead = async (data) => {
  const response = await api.post('/api/leads/research', data)
  return response.data
}

export const getLeads = async (params = {}) => {
  const response = await api.get('/api/leads', { params })
  return response.data
}

export default api
 