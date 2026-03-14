import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { payrollService } from '@/services/payroll'

const STORAGE_KEY = 'gym_payroll_session'

export const usePayrollStore = defineStore('payroll', () => {
  const records  = ref([])
  const loading  = ref(false)
  const error    = ref(null)

  // ── Estado persistente de la sesión de nómina ─────────────────────────────
  const session = ref(cargarSesion())

  function cargarSesion() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY)
      return raw ? JSON.parse(raw) : sesionVacia()
    } catch {
      return sesionVacia()
    }
  }

  function sesionVacia() {
    return {
      fecha:   '',
      period:  '',
      form: {
        employee:          '',
        viatico:           0,
        otras_deducciones: 0,
        prestamo_adelanto: 0,
        notes:             ''
      },
      editando: null,
    }
  }

  // Cada vez que cambia la sesión → guardar en localStorage
  watch(session, (val) => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(val))
  }, { deep: true })

  function guardarSesion(datos) {
    session.value = { ...session.value, ...datos }
  }

  function limpiarSesion() {
    session.value = sesionVacia()
    localStorage.removeItem(STORAGE_KEY)
  }

  // ── Records ───────────────────────────────────────────────────────────────
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
    session, guardarSesion, limpiarSesion, sesionVacia,
    fetchAll, generate, exportCSV
  }
})