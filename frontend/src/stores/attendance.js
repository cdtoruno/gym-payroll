import { defineStore } from 'pinia'
import { ref } from 'vue'
import { attendanceService } from '@/services/attendance'

export const useAttendanceStore = defineStore('attendance', () => {
  const records  = ref([])
  const summary  = ref([])
  const loading  = ref(false)
  const error    = ref(null)

  async function fetchAll(params = {}) {
    loading.value = true
    error.value   = null
    try {
      const res    = await attendanceService.getAll(params)
      records.value = res.data.results ?? res.data
    } catch (e) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function fetchSummary(params = {}) {
    loading.value = true
    error.value   = null
    try {
      const res    = await attendanceService.getSummary(params)
      summary.value = res.data
    } catch (e) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function register(data) {
    const res = await attendanceService.register(data)
    records.value.unshift(res.data)
    return res.data
  }

  return {
    records, summary, loading, error,
    fetchAll, fetchSummary, register
  }
})