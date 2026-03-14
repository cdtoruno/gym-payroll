import api from './api'

export const payrollService = {
  getAll(params = {})    { return api.get('/payroll/', { params }) },
  generate(data)         { return api.post('/payroll/generate/', data) },
  exportCSV(params = {}) {
    return api.get('/payroll/export/', {
      params,
      responseType: 'blob'
    })
  }
}