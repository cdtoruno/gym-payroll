import api from './api'

export const vacationsService = {
  getAll(params = {})  { return api.get('/vacations/', { params }) },
  getById(id)          { return api.get(`/vacations/${id}/`) },
  create(data)         { return api.post('/vacations/', data) },
  update(id, data)     { return api.put(`/vacations/${id}/`, data) }
}