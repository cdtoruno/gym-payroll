<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-2xl font-bold text-gray-900">Vacaciones</h1>
      <p class="text-sm text-gray-500 mt-1">
        Gestión de días de vacaciones por empleado
      </p>
    </div>

    <AlertMessage :message="vacStore.error" type="error" />

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Formulario registrar falta -->
      <div class="card space-y-4">
        <h2 class="text-base font-semibold text-gray-900">Registrar falta por vacaciones</h2>
        <p class="text-xs text-gray-400">
          El descuento se aplicará automáticamente en el siguiente Q1.
        </p>

        <AlertMessage :message="formError"   type="error"   />
        <AlertMessage :message="formSuccess" type="success" />

        <div>
          <label class="label">Empleado *</label>
          <select v-model="form.employee_id" class="input" required>
            <option value="">— Selecciona —</option>
            <option v-for="e in empStore.activeEmployees" :key="e.id" :value="e.id">
              {{ e.name }}
            </option>
          </select>
        </div>

        <div>
          <label class="label">Fecha de la falta *</label>
          <input v-model="form.fecha" class="input" type="date" required />
        </div>

        <div>
          <label class="label">Motivo</label>
          <input v-model="form.motivo" class="input" type="text"
                 placeholder="Falta por vacaciones" />
        </div>

        <!-- Preview del impacto -->
        <div v-if="vacacionesEmpleado"
             class="rounded-xl bg-amber-50 border border-amber-100 p-4 text-sm">
          <p class="font-semibold text-amber-700 mb-2">Impacto en siguiente Q1</p>
          <div class="grid grid-cols-2 gap-y-1 text-amber-800">
            <span>Días disponibles</span>
            <span class="text-right font-medium">{{ vacacionesEmpleado.dias_disponibles }}</span>
            <span>Faltas pendientes</span>
            <span class="text-right font-medium text-red-600">
              {{ vacacionesEmpleado.dias_falta_pendiente }}
              → {{ vacacionesEmpleado.dias_falta_pendiente + 1 }}
            </span>
            <span>Días a pagar</span>
            <span class="text-right font-medium">
              {{ Math.max(0, vacacionesEmpleado.dias_a_pagar - 1) }}
            </span>
            <span>Monto siguiente Q1</span>
            <span class="text-right font-medium">
              {{ fmt(vacacionesEmpleado.monto_vacaciones / 2) }}
            </span>
          </div>
        </div>

        <button class="btn-primary w-full justify-center"
                :disabled="saving || !form.employee_id || !form.fecha"
                @click="registrarFalta">
          Registrar falta
        </button>
      </div>

      <!-- Tabla registros -->
      <div class="card p-0 overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-100">
          <h2 class="text-base font-semibold text-gray-900">Estado actual de vacaciones</h2>
        </div>
        <LoadingSpinner v-if="vacStore.loading" />
        <div v-else-if="!vacStore.vacations.length"
             class="text-center py-12 text-gray-400 text-sm">
          No hay registros de vacaciones aún.
        </div>
        <table v-else class="w-full text-sm">
          <thead class="border-b border-gray-100 bg-gray-50">
            <tr>
              <th class="table-th">Empleado</th>
              <th class="table-th text-center">Disponibles</th>
              <th class="table-th text-center">Faltas</th>
              <th class="table-th text-center">A pagar</th>
              <th class="table-th text-right">Monto Q1</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr v-for="v in vacStore.vacations" :key="v.id"
                class="hover:bg-gray-50">
              <td class="table-td font-medium">{{ v.employee_name }}</td>
              <td class="table-td text-center">
                <span class="badge badge-blue">{{ v.dias_disponibles }}</span>
              </td>
              <td class="table-td text-center">
                <span :class="v.dias_falta_pendiente > 0 ? 'badge-red' : 'badge-green'">
                  {{ v.dias_falta_pendiente }}
                </span>
              </td>
              <td class="table-td text-center">
                <span :class="v.dias_a_pagar > 0 ? 'badge-green' : 'badge-red'">
                  {{ v.dias_a_pagar }}
                </span>
              </td>
              <td class="table-td text-right font-semibold">
                {{ fmt(v.monto_vacaciones) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AlertMessage   from '@/components/ui/AlertMessage.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import { useEmployeesStore } from '@/stores/employees'
import { useVacationsStore  } from '@/stores/vacations'
import api from '@/services/api'

const empStore = useEmployeesStore()
const vacStore = useVacationsStore()

const formError   = ref('')
const formSuccess = ref('')
const saving      = ref(false)

const form = ref({
  employee_id: '',
  fecha:       '',
  motivo:      'Falta por vacaciones'
})

const fmt = (n) =>
  new Intl.NumberFormat('es-NI', { style: 'currency', currency: 'NIO' }).format(n)

// Muestra el estado actual de vacaciones del empleado seleccionado
const vacacionesEmpleado = computed(() =>
  vacStore.vacations.find(v => v.employee === form.value.employee_id) || null
)

async function registrarFalta() {
  if (!form.value.employee_id) {
    formError.value = 'Debes seleccionar un empleado.'
    return
  }
  if (!form.value.fecha) {
    formError.value = 'Debes seleccionar una fecha.'
    return
  }

  formError.value   = ''
  formSuccess.value = ''
  saving.value      = true

  try {
    const res = await api.post('/vacations/falta/', {
      employee_id: form.value.employee_id,
      fecha:       form.value.fecha,
      motivo:      form.value.motivo,
    })
    formSuccess.value = res.data.message
    form.value = { employee_id: '', fecha: '', motivo: 'Falta por vacaciones' }
    await vacStore.fetchAll()
  } catch (e) {
    formError.value = e.message
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  if (!empStore.employees.length) await empStore.fetchAll()
  await vacStore.fetchAll()
})
</script>