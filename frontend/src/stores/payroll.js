import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { payrollService } from '@/services/payroll'

export const usePayrollStore = defineStore('payroll', () => {
  const records  = ref([])
  const loading  = ref(false)
  const error    = ref(null)

  const lastPayrollDate = computed(() => {
    if (!records.value.length) return null
    return records.value[0].date
  })

  async function fetchAll(params = {}) {
    loading.value = true
    error.value   = null
    try {
      const res = await payrollService.getAll(params)
      records.value = res.data.results ?? res.data
    } catch (e) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function generate(data) {
    loading.value = true
    error.value   = null
    try {
      const res = await payrollService.generate(data)
      records.value.unshift(res.data)
      return res.data
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function exportCSV(params = {}) {
    const res  = await payrollService.exportCSV(params)
    const url  = URL.createObjectURL(new Blob([res.data]))
    const link = document.createElement('a')
    link.href  = url
    link.download = `nomina_${new Date().toISOString().slice(0, 10)}.csv`
    link.click()
    URL.revokeObjectURL(url)
  }

  return {
    records, loading, error, lastPayrollDate,
    fetchAll, generate, exportCSV
  }
})