<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Historial de Nómina</h1>
        <p class="text-sm text-gray-500 mt-1">{{ store.records.length }} registros</p>
      </div>
      <button class="btn-secondary" :disabled="!store.records.length || exporting"
              @click="exportCSV">
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
        </svg>
        {{ exporting ? 'Exportando...' : 'Exportar Excel' }}
      </button>
    </div>

    <!-- Filtros por mes y quincena -->
    <div class="card py-4">
      <div class="flex flex-wrap gap-4 items-end">

        <!-- Mes -->
        <div>
          <label class="label">Mes</label>
          <select v-model="filters.month" class="input w-40">
            <option value="">Todos</option>
            <option v-for="m in meses" :key="m.value" :value="m.value">
              {{ m.label }}
            </option>
          </select>
        </div>

        <!-- Año -->
        <div>
          <label class="label">Año</label>
          <select v-model="filters.year" class="input w-32">
            <option value="">Todos</option>
            <option v-for="y in anios" :key="y" :value="y">{{ y }}</option>
          </select>
        </div>

        <!-- Quincena -->
        <div>
          <label class="label">Quincena</label>
          <select v-model="filters.period" class="input w-52">
            <option value="">Ambas quincenas</option>
            <option :value="1">Primera quincena (1–15)</option>
            <option :value="2">Segunda quincena (16–fin)</option>
          </select>
        </div>

        <!-- Empleado -->
        <div>
          <label class="label">Empleado</label>
          <select v-model="filters.employee" class="input w-52">
            <option value="">Todos los empleados</option>
            <option v-for="e in empStore.employees" :key="e.id" :value="e.id">
              {{ e.name }}
            </option>
          </select>
        </div>

        <button class="btn-primary" @click="applyFilters">Buscar</button>
        <button class="btn-secondary" @click="resetFilters">Limpiar</button>
      </div>
    </div>

    <AlertMessage :message="store.error" type="error" />

    <!-- Tabla -->
    <div class="card p-0 overflow-hidden">
      <LoadingSpinner v-if="store.loading" />
      <div v-else-if="!store.records.length"
           class="text-center py-16 text-gray-400 text-sm">
        No hay registros para el período seleccionado.
      </div>
      <div v-else class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="border-b border-gray-100 bg-gray-50">
            <tr>
              <th class="table-th">Empleado</th>
              <th class="table-th">Cédula</th>
              <th class="table-th">Fecha</th>
              <th class="table-th text-center">Quincena</th>
              <th class="table-th text-center">Días</th>
              <th class="table-th text-right">Salario</th>
              <th class="table-th text-right">Vacaciones</th>
              <th class="table-th text-right">Viático</th>
              <th class="table-th text-right">Sub-total</th>
              <th class="table-th text-right">Otras dedu.</th>
              <th class="table-th text-right">Préstamo</th>
              <th class="table-th text-right">Total</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr v-for="r in store.records" :key="r.id" class="hover:bg-gray-50">
              <td class="table-td font-medium">{{ r.employee_name }}</td>
              <td class="table-td text-gray-500 font-mono text-xs">
                {{ r.employee_cedula || '—' }}
              </td>
              <td class="table-td text-gray-500">{{ formatDate(r.date) }}</td>
              <td class="table-td text-center">
                <span class="badge"
                      :class="r.period === 1 ? 'badge-blue' : 'badge-yellow'">
                  {{ r.period === 1 ? 'Q1 (1–15)' : 'Q2 (16–fin)' }}
                </span>
              </td>
              <td class="table-td text-center">{{ r.dias_laborados }}</td>
              <td class="table-td text-right">{{ fmt(r.salary_base) }}</td>
              <td class="table-td text-right text-purple-600">
                {{ r.vacation_payment > 0 ? fmt(r.vacation_payment) : '—' }}
              </td>
              <td class="table-td text-right text-green-600">
                {{ r.viatico > 0 ? fmt(r.viatico) : '—' }}
              </td>
              <td class="table-td text-right font-medium">{{ fmt(r.sub_total) }}</td>
              <td class="table-td text-right text-red-500">
                {{ r.otras_deducciones > 0 ? fmt(r.otras_deducciones) : '—' }}
              </td>
              <td class="table-td text-right text-red-500">
                {{ r.prestamo_adelanto > 0 ? fmt(r.prestamo_adelanto) : '—' }}
              </td>
              <td class="table-td text-right font-bold text-gray-900">
                {{ fmt(r.total) }}
              </td>
            </tr>
          </tbody>

          <!-- Totales -->
          <tfoot class="border-t-2 border-gray-200 bg-gray-50">
            <tr>
              <td class="table-td font-semibold text-gray-700" colspan="5">
                Total del período
              </td>
              <td class="table-td text-right font-semibold">
                {{ fmt(sum('salary_base')) }}
              </td>
              <td class="table-td text-right font-semibold text-purple-700">
                {{ fmt(sum('vacation_payment')) }}
              </td>
              <td class="table-td text-right font-semibold text-green-700">
                {{ fmt(sum('viatico')) }}
              </td>
              <td class="table-td text-right font-semibold">
                {{ fmt(sum('sub_total')) }}
              </td>
              <td class="table-td text-right font-semibold text-red-600">
                {{ fmt(sum('otras_deducciones')) }}
              </td>
              <td class="table-td text-right font-semibold text-red-600">
                {{ fmt(sum('prestamo_adelanto')) }}
              </td>
              <td class="table-td text-right font-bold text-blue-700 text-base">
                {{ fmt(sum('total')) }}
              </td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AlertMessage   from '@/components/ui/AlertMessage.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import { usePayrollStore    } from '@/stores/payroll'
import { useEmployeesStore  } from '@/stores/employees'

const store    = usePayrollStore()
const empStore = useEmployeesStore()
const exporting = ref(false)

const filters = ref({
  month:    '',
  year:     new Date().getFullYear(),
  period:   '',
  employee: '',
})

// ── Catálogos ─────────────────────────────────────────────────────────────────
const meses = [
  { value:  1, label: 'Enero'      },
  { value:  2, label: 'Febrero'    },
  { value:  3, label: 'Marzo'      },
  { value:  4, label: 'Abril'      },
  { value:  5, label: 'Mayo'       },
  { value:  6, label: 'Junio'      },
  { value:  7, label: 'Julio'      },
  { value:  8, label: 'Agosto'     },
  { value:  9, label: 'Septiembre' },
  { value: 10, label: 'Octubre'    },
  { value: 11, label: 'Noviembre'  },
  { value: 12, label: 'Diciembre'  },
]

const anios = computed(() => {
  const actual = new Date().getFullYear()
  return [actual, actual - 1, actual - 2]
})

// ── Etiqueta legible del período buscado ──────────────────────────────────────
const labelPeriodo = computed(() => {
  const mes    = meses.find(m => m.value === filters.value.month)
  const anio   = filters.value.year
  const q      = filters.value.period

  if (!mes && !anio && !q) return ''

  let label = ''
  if (q === 1)  label = 'Primera quincena'
  if (q === 2)  label = 'Segunda quincena'
  if (!q)       label = 'Ambas quincenas'

  if (mes)  label += ` de ${mes.label}`
  if (anio) label += ` ${anio}`

  return label
})

// ── Formateo ──────────────────────────────────────────────────────────────────
const fmt = (n) =>
  new Intl.NumberFormat('es-NI', { style: 'currency', currency: 'NIO' }).format(n || 0)

const formatDate = (dateStr) => {
  if (!dateStr) return '—'
  const [year, month, day] = dateStr.split('-')
  const mes = meses.find(m => m.value === parseInt(month))
  return `${parseInt(day)} de ${mes?.label} ${year}`
}

const sum = (field) =>
  store.records.reduce((acc, r) => acc + parseFloat(r[field] || 0), 0)

// ── Convertir mes+año a rango de fechas ───────────────────────────────────────
function buildParams() {
  const params = {}

  if (filters.value.period)   params.period   = filters.value.period
  if (filters.value.employee) params.employee = filters.value.employee

  if (filters.value.year && filters.value.month) {
    const y = filters.value.year
    const m = String(filters.value.month).padStart(2, '0')

    if (filters.value.period == 1) {
      // Q1: días 1–15
      params.date_from = `${y}-${m}-01`
      params.date_to   = `${y}-${m}-15`
    } else if (filters.value.period == 2) {
      // Q2: días 16–fin
      const lastDay = new Date(y, filters.value.month, 0).getDate()
      params.date_from = `${y}-${m}-16`
      params.date_to   = `${y}-${m}-${lastDay}`
    } else {
      // Ambas quincenas del mes
      const lastDay = new Date(y, filters.value.month, 0).getDate()
      params.date_from = `${y}-${m}-01`
      params.date_to   = `${y}-${m}-${lastDay}`
    }
  } else if (filters.value.year && !filters.value.month) {
    // Todo el año
    params.date_from = `${filters.value.year}-01-01`
    params.date_to   = `${filters.value.year}-12-31`
  }

  return params
}

async function applyFilters() {
  await store.fetchAll(buildParams())
}

async function resetFilters() {
  filters.value = {
    month:    '',
    year:     new Date().getFullYear(),
    period:   '',
    employee: '',
  }
  await store.fetchAll()
}

async function exportCSV() {
  exporting.value = true
  try {
    await store.exportCSV(buildParams())
  } finally {
    exporting.value = false
  }
}

onMounted(async () => {
  if (!empStore.employees.length) await empStore.fetchAll()
  await store.fetchAll()
})
</script>
