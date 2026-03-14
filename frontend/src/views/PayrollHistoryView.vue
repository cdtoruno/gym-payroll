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
        {{ exporting ? 'Exportando...' : 'Exportar CSV' }}
      </button>
    </div>

    <!-- Filtros -->
    <div class="card py-4">
      <div class="flex flex-wrap gap-4 items-end">
        <div>
          <label class="label">Período</label>
          <select v-model="filters.period" class="input w-48">
            <option value="">Todos</option>
            <option :value="1">Primera quincena</option>
            <option :value="2">Segunda quincena</option>
          </select>
        </div>
        <div>
          <label class="label">Desde</label>
          <input v-model="filters.date_from" class="input" type="date" />
        </div>
        <div>
          <label class="label">Hasta</label>
          <input v-model="filters.date_to" class="input" type="date" />
        </div>
        <button class="btn-primary" @click="applyFilters">Filtrar</button>
        <button class="btn-secondary" @click="resetFilters">Limpiar</button>
      </div>
    </div>

    <AlertMessage :message="store.error" type="error" />

    <!-- Tabla -->
    <div class="card p-0 overflow-hidden">
      <LoadingSpinner v-if="store.loading" />
      <div v-else-if="!store.records.length"
           class="text-center py-16 text-gray-400 text-sm">
        No hay registros de nómina.
      </div>
      <div v-else class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="border-b border-gray-100 bg-gray-50">
            <tr>
              <th class="table-th">Empleado</th>
              <th class="table-th">Cédula</th>
              <th class="table-th">Fecha</th>
              <th class="table-th text-center">Período</th>
              <th class="table-th text-center">Días</th>
              <th class="table-th text-right">Salario</th>
              <th class="table-th text-right">Vacaciones</th>
              <th class="table-th text-right">Viático</th>
              <th class="table-th text-right">Sub-total</th>
              <th class="table-th text-right">Otras Dedu.</th>
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
              <td class="table-td text-gray-500">{{ r.date }}</td>
              <td class="table-td text-center">
                <span class="badge"
                      :class="r.period === 1 ? 'badge-blue' : 'badge-yellow'">
                  {{ r.period === 1 ? 'Q1' : 'Q2' }}
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
          <!-- Fila de totales -->
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
import { ref, onMounted } from 'vue'
import AlertMessage   from '@/components/ui/AlertMessage.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import { usePayrollStore } from '@/stores/payroll'

const store     = usePayrollStore()
const exporting = ref(false)
const filters   = ref({ period: '', date_from: '', date_to: '' })

const fmt = (n) =>
  new Intl.NumberFormat('es-NI', { style: 'currency', currency: 'NIO' }).format(n)

const sum = (field) =>
  store.records.reduce((acc, r) => acc + parseFloat(r[field] || 0), 0)

async function applyFilters() {
  const params = {}
  if (filters.value.period)    params.period    = filters.value.period
  if (filters.value.date_from) params.date_from = filters.value.date_from
  if (filters.value.date_to)   params.date_to   = filters.value.date_to
  await store.fetchAll(params)
}

async function resetFilters() {
  filters.value = { period: '', date_from: '', date_to: '' }
  await store.fetchAll()
}

async function exportCSV() {
  exporting.value = true
  try {
    await store.exportCSV(filters.value)
  } finally {
    exporting.value = false
  }
}

onMounted(() => store.fetchAll())
</script>