import axios from 'axios'
import type { User } from '../types'

const configuredApiUrl = import.meta.env.VITE_API_URL?.trim()
const developmentApiUrl = 'http://localhost:8000/api/v1/'

// Vite embeds this value at build time. Set VITE_API_URL in Vercel to the
// public Render URL, including `/api/v1/` (for example,
// `https://hireflow-api.onrender.com/api/v1/`).
if (!configuredApiUrl && !import.meta.env.DEV) {
  console.error('VITE_API_URL is not configured. API requests cannot reach the production backend.')
}

const apiBaseUrl = (configuredApiUrl || developmentApiUrl).replace(/\/?$/, '/')

export const api = axios.create({ baseURL: apiBaseUrl })
api.interceptors.request.use((config) => { const token = localStorage.getItem('hireflow_access'); if (token) config.headers.Authorization = `Bearer ${token}`; return config })
api.interceptors.response.use((response) => response, async (error) => { const request = error.config; if (error.response?.status === 401 && !request._retry && localStorage.getItem('hireflow_refresh')) { request._retry = true; try { const { data } = await axios.post(`${api.defaults.baseURL}auth/refresh/`, { refresh: localStorage.getItem('hireflow_refresh') }); localStorage.setItem('hireflow_access', data.access); request.headers.Authorization = `Bearer ${data.access}`; return api(request) } catch { localStorage.clear(); window.location.assign('/login') } } return Promise.reject(error) })
export const getError = (error: unknown) => { const data = (error as {response?: {data?: Record<string, string[]|string>}}).response?.data; if (!data) return 'Something went wrong. Please try again.'; return Object.values(data).flat().join(' ') || 'Request failed.' }
export const auth = { me: () => api.get<User>('auth/me/').then(r => r.data), login: (email:string,password:string) => api.post('auth/login/', {username: email, password}).then(r => r.data), register: (payload: Record<string,string>) => api.post<User>('auth/register/',payload).then(r=>r.data) }
