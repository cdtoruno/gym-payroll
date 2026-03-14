<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-2xl font-bold text-gray-900">Dashboard</h1>
      <p class="text-sm text-gray-500 mt-1">Resumen del sistema de nómina</p>
    </div>

    <!-- Stat cards -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <div class="card flex items-center gap-4">
        <div class="p-3 rounded-xl bg-blue-100 text-blue-600">
          <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/>
          </svg>
        </div>
        <div>
          <p class="text-sm text-gray-500">Empleados activos</p>
          <p class="text-3xl font-bold text-gray-900">{{ empStore.activeEmployees.length }}</p>
        </div>
      </div>

      <div class="card flex items-center gap-4">
        <div class="p-3 rounded-xl bg-green-100 text-green-600">
          <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
          </svg>
        </div>
        <div>
          <p class="text-sm text-gray-500">Última nómina</p>
          <p class="text-xl font-bold text-gray-900">
            {{ payStore.lastPayrollDate ?? '—' }}
          </p>
        </div>
      </div>

      <div class="card flex items-center gap-4">
        <div class="p-3 rounded-xl bg-purple-100 text-purple-600">
          <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"/>
          </svg>
        </div>
        <div>
          <p class="text-sm text-gray-500">Nóminas generadas</p>
          <p class="text-3xl font-bold text-gray-900">{{ payStore.records.length }}</p>
        </div>
      </div>
    </div>

    <!-- Acciones rápidas -->
    <div class="card">
      <h2 class="text-base font-semibold text-gray-900 mb-4">Acciones rápidas</h2>
      <div class="flex flex-wrap gap-3">
        <RouterLink to="/payroll" class="btn-primary">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
          </svg>
          Generar nómina
        </RouterLink>
        <RouterLink to="/employees" class="btn-secondary">Ver empleados</RouterLink>
        <RouterLink to="/payroll/history" class="btn-secondary">Ver historial</RouterLink>
      </div>
    </div>

    <!-- Últimas nóminas -->
    <div class="card">
      <h2 class="text-base font-semibold text-gray-900 mb-4">Últimas nóminas</h2>
      <LoadingSpinner v-if="payStore.loading" />
      <div v-else-if="!payStore.records.length"
           class="text-center py-8 text-gray-400 text-sm">
        No hay nóminas registradas aún.
      </div>
      <div v-else class="overflow-x-auto">
        <table class="w-full">
          <thead class="border-b border-gray-100">
            <tr>
              <th class="table-th">Empleado</th>
              <th class="table-th">Fecha</th>
              <th class="table-th">Período</th>
              <th class="table-th text-right">Total</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr v-for="r in payStore.records.slice(0, 5)" :key="r.id"
                class="hover:bg-gray-50">
              <td class="table-td font-medium">{{ r.employee_name }}</td>
              <td class="table-td">{{ r.date }}</td>
              <td class="table-td">
                <span class="badge" :class="r.period === 1 ? 'badge-blue' : 'badge-yellow'">
                  {{ r.period === 1 ? 'Q1' : 'Q2' }}
                </span>
              </td>
              <td class="table-td text-right font-semibold">{{ fmt(r.total) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import { useEmployeesStore } from '@/stores/employees'
import { usePayrollStore    } from '@/stores/payroll'

const empStore = useEmployeesStore()
const payStore = usePayrollStore()

const fmt = (n) =>
  new Intl.NumberFormat('es-NI', { style: 'currency', currency: 'NIO' }).format(n)

onMounted(async () => {
  if (!empStore.employees.length) await empStore.fetchAll()
  if (!payStore.records.length)   await payStore.fetchAll()
})
</script>