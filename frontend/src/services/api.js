import axios from 'axios'

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api',
  headers: { 'Content-Type': 'application/json' },
  timeout: 10000
})

// Interceptor — normaliza errores para mostrarlos en la UI
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail ||
      error.response?.data?.error ||
      Object.values(error.response?.data || {})[0]?.[0] ||
      'Error de conexión con el servidor'
    return Promise.reject(new Error(message))
  }
)

export default api