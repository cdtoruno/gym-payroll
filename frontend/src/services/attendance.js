import api from './api'

export const attendanceService = {
  getAll(params = {})    { return api.get('/attendance/', { params }) },
  getSummary(params = {}) { return api.get('/attendance/summary/', { params }) },
  register(data)         { return api.post('/attendance/register/', data) },
}