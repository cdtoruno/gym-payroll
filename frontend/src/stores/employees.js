import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { employeesService } from '@/services/employees'

export const useEmployeesStore = defineStore('employees', () => {
  const employees = ref([])
  const loading   = ref(false)
  const error     = ref(null)
  const search    = ref('')

  const filtered = computed(() => {
    if (!search.value.trim()) return employees.value
    const q = search.value.toLowerCase()
    return employees.value.filter(e =>
      e.name.toLowerCase().includes(q) ||
      e.position.toLowerCase().includes(q) ||
      e.cedula.includes(q) ||
      e.phone.includes(q)
    )
  })

  const activeEmployees = computed(() =>
    employees.value.filter(e => e.active)
  )

  async function fetchAll() {
    loading.value = true
    error.value   = null
    try {
      const res = await employeesService.getAll()
      employees.value = res.data.results ?? res.data
    } catch (e) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function create(data) {
    const res = await employeesService.create(data)
    employees.value.push(res.data)
    return res.data
  }

  async function update(id, data) {
    const res = await employeesService.update(id, data)
    const idx = employees.value.findIndex(e => e.id === id)
    if (idx !== -1) employees.value[idx] = res.data
    return res.data
  }

  async function remove(id) {
    await employeesService.remove(id)
    const idx = employees.value.findIndex(e => e.id === id)
    if (idx !== -1) employees.value[idx].active = false
  }

  return {
    employees, loading, error, search,
    filtered, activeEmployees,
    fetchAll, create, update, remove
  }
})