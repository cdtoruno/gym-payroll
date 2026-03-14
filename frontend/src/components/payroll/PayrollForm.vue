<template>
  <div class="card space-y-5">
    <h2 class="text-lg font-semibold text-gray-900">Generar nómina</h2>

    <AlertMessage :message="error"   type="error"   />
    <AlertMessage :message="success" type="success" />

    <div class="grid grid-cols-2 gap-4">
      <!-- Empleado -->
      <div class="col-span-2">
        <label class="label">Empleado *</label>
        <select v-model="form.employee" class="input" required>
          <option value="">— Selecciona un empleado —</option>
          <option v-for="e in empStore.activeEmployees" :key="e.id" :value="e.id">
            {{ e.name }} — {{ e.position }}
          </option>
        </select>
      </div>

      <!-- Fecha -->
      <div>
        <label class="label">Fecha *</label>
        <input v-model="form.date" class="input" type="date" required />
      </div>

      <!-- Período -->
      <div>
        <label class="label">Período *</label>
        <select v-model="form.period" class="input" required>
          <option value="">— Selecciona —</option>
          <option :value="1">Primera quincena (1–15)</option>
          <option :value="2">Segunda quincena (16–fin)</option>
        </select>
      </div>

      <!-- Días laborados -->
      <div>
        <label class="label">Días laborados</label>
        <input v-model="form.dias_laborados" class="input" type="number"
               min="1" max="15" placeholder="15" />
      </div>

      <!-- Viático -->
      <div>
        <label class="label">Viático</label>
        <div class="relative">
          <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm">C$</span>
          <input v-model="form.viatico" class="input pl-9" type="number"
                 min="0" step="0.01" placeholder="0.00" />
        </div>
      </div>

      <!-- Otras deducciones -->
      <div>
        <label class="label">Otras deducciones</label>
        <div class="relative">
          <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm">C$</span>
          <input v-model="form.otras_deducciones" class="input pl-9" type="number"
                 min="0" step="0.01" placeholder="0.00" />
        </div>
      </div>

      <!-- Préstamo / Adelanto -->
      <div>
        <label class="label">Deduc. Préstamo / Adelanto</label>
        <div class="relative">
          <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm">C$</span>
          <input v-model="form.prestamo_adelanto" class="input pl-9" type="number"
                 min="0" step="0.01" placeholder="0.00" />
        </div>
      </div>

      <!-- Notas -->
      <div class="col-span-2">
        <label class="label">Notas</label>
        <textarea v-model="form.notes" class="input resize-none" rows="2"
                  placeholder="Opcional…" />
      </div>
    </div>

    <!-- Preview del total -->
    <div v-if="selectedEmployee" class="rounded-xl bg-blue-50 border border-blue-100 p-4">
      <p class="text-xs font-semibold text-blue-600 uppercase tracking-wider mb-3">
        Vista previa del cálculo
      </p>
      <div class="grid grid-cols-2 gap-y-2 text-sm">
        <span class="text-gray-600">Salario ordinario</span>
        <span class="text-right font-medium">{{ fmt(selectedEmployee.salary_base) }}</span>

        <template v-if="form.period == 1">
          <span class="text-gray-600">Vacaciones (÷6)</span>
          <span class="text-right font-medium text-purple-600">
            + {{ fmt(vacaciones) }}
          </span>
        </template>

        <span class="text-gray-600">Viático</span>
        <span class="text-right font-medium text-green-600">
          + {{ fmt(form.viatico || 0) }}
        </span>

        <span class="text-gray-600 font-medium">Sub-total devengado</span>
        <span class="text-right font-semibold">{{ fmt(subTotal) }}</span>

        <span class="text-gray-600">Otras deducciones</span>
        <span class="text-right font-medium text-red-500">
          − {{ fmt(form.otras_deducciones || 0) }}
        </span>

        <span class="text-gray-600">Préstamo / Adelanto</span>
        <span class="text-right font-medium text-red-500">
          − {{ fmt(form.prestamo_adelanto || 0) }}
        </span>

        <div class="col-span-2 border-t border-blue-200 pt-2 mt-1 flex justify-between">
          <span class="font-bold text-gray-900">Total devengado</span>
          <span class="font-bold text-xl text-blue-700">{{ fmt(total) }}</span>
        </div>
      </div>
    </div>

    <button class="btn-primary w-full justify-center py-3"
            :disabled="!isValid || loading" @click="submit">
      <svg v-if="loading" class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10"
                stroke="currentColor" stroke-width="4"/>
        <path class="opacity-75" fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
      </svg>
      Generar nómina
    </button>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import AlertMessage from '@/components/ui/AlertMessage.vue'
import { useEmployeesStore } from '@/stores/employees'
import { usePayrollStore    } from '@/stores/payroll'

const empStore  = useEmployeesStore()
const payStore  = usePayrollStore()

const error   = ref('')
const success = ref('')
const loading = ref(false)

const form = ref({
  employee: '', date: '', period: '',
  dias_laborados: 15, viatico: 0,
  otras_deducciones: 0, prestamo_adelanto: 0, notes: ''
})

const selectedEmployee = computed(() =>
  empStore.activeEmployees.find(e => e.id === form.value.employee) || null
)

const vacaciones = computed(() => {
  if (!selectedEmployee.value || form.value.period != 1) return 0
  return parseFloat(selectedEmployee.value.salary_base) / 6
})

const subTotal = computed(() => {
  if (!selectedEmployee.value) return 0
  return parseFloat(selectedEmployee.value.salary_base)
    + vacaciones.value
    + parseFloat(form.value.viatico || 0)
})

const total = computed(() => {
  return subTotal.value
    - parseFloat(form.value.otras_deducciones || 0)
    - parseFloat(form.value.prestamo_adelanto || 0)
})

const isValid = computed(() =>
  form.value.employee && form.value.date && form.value.period !== ''
)

const fmt = (n) =>
  new Intl.NumberFormat('es-NI', { style: 'currency', currency: 'NIO' }).format(n)

async function submit() {
  error.value   = ''
  success.value = ''
  loading.value = true
  try {
    await payStore.generate({
      employee:          form.value.employee,
      date:              form.value.date,
      period:            form.value.period,
      dias_laborados:    form.value.dias_laborados    || 15,
      viatico:           form.value.viatico           || 0,
      otras_deducciones: form.value.otras_deducciones || 0,
      prestamo_adelanto: form.value.prestamo_adelanto || 0,
      notes:             form.value.notes
    })
    success.value = '¡Nómina generada correctamente!'
    form.value = {
      employee: '', date: '', period: '',
      dias_laborados: 15, viatico: 0,
      otras_deducciones: 0, prestamo_adelanto: 0, notes: ''
    }
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>