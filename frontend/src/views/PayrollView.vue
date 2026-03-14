<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-2xl font-bold text-gray-900">Generar Nómina</h1>
      <p class="text-sm text-gray-500 mt-1">
        Calcula y registra el pago quincenal de un empleado
      </p>
    </div>

    <div class="max-w-xl">
      <PayrollForm />
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import PayrollForm from '@/components/payroll/PayrollForm.vue'
import { useEmployeesStore } from '@/stores/employees'
import { useVacationsStore  } from '@/stores/vacations'

const empStore = useEmployeesStore()
const vacStore = useVacationsStore()

onMounted(async () => {
  if (!empStore.employees.length) await empStore.fetchAll()
  if (!vacStore.vacations.length) await vacStore.fetchAll()
})
</script>