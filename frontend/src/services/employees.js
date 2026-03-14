import api from './api'

export const employeesService = {
  getAll(params = {})  { return api.get('/employees/', { params }) },
  getById(id)          { return api.get(`/employees/${id}/`) },
  create(data)         { return api.post('/employees/', data) },
  update(id, data)     { return api.put(`/employees/${id}/`, data) },
  remove(id)           { return api.delete(`/employees/${id}/`) }
}