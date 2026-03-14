import { defineStore } from 'pinia'
import { ref } from 'vue'
import { vacationsService } from '@/services/vacations'

export const useVacationsStore = defineStore('vacations', () => {
  const vacations = ref([])
  const loading   = ref(false)
  const error     = ref(null)

  async function fetchAll() {
    loading.value = true
    error.value   = null
    try {
      const res = await vacationsService.getAll()
      vacations.value = res.data.results ?? res.data
    } catch (e) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function save(data) {
    const existing = vacations.value.find(v => v.employee === data.employee)
    let res
    if (existing) {
      res = await vacationsService.update(existing.id, data)
      const idx = vacations.value.findIndex(v => v.id === existing.id)
      vacations.value[idx] = res.data
    } else {
      res = await vacationsService.create(data)
      vacations.value.push(res.data)
    }
    return res.data
  }

  return { vacations, loading, error, fetchAll, save }
})