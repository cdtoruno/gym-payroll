<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Empleados</h1>
        <p class="text-sm text-gray-500 mt-1">{{ store.filtered.length }} empleados</p>
      </div>
      <button class="btn-primary" @click="openCreate">
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
        </svg>
        Nuevo empleado
      </button>
    </div>

    <!-- Búsqueda -->
    <div class="relative max-w-xs">
      <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400"
           fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0"/>
      </svg>
      <input v-model="store.search" class="input pl-9" type="search"
             placeholder="Buscar por nombre, cédula o cargo..." />
    </div>

    <AlertMessage :message="store.error" type="error" />

    <!-- Tabla -->
    <div class="card p-0 overflow-hidden">
      <LoadingSpinner v-if="store.loading" />
      <div v-else-if="!store.filtered.length"
           class="text-center py-16 text-gray-400">
        <svg class="w-12 h-12 mx-auto mb-3 text-gray-300" fill="none"
             viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
            d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/>
        </svg>
        <p class="text-sm">No se encontraron empleados.</p>
      </div>
      <div v-else class="overflow-x-auto">
        <table class="w-full">
          <thead class="border-b border-gray-100 bg-gray-50">
            <tr>
              <th class="table-th">Nombre</th>
              <th class="table-th">Cédula</th>
              <th class="table-th">Cargo</th>
              <th class="table-th">Teléfono</th>
              <th class="table-th text-right">Salario base</th>
              <th class="table-th">Contratación</th>
              <th class="table-th">Estado</th>
              <th class="table-th w-24">Acciones</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr v-for="emp in store.filtered" :key="emp.id"
                class="hover:bg-gray-50 transition-colors">
              <td class="table-td font-medium text-gray-900">{{ emp.name }}</td>
              <td class="table-td text-gray-500 font-mono text-xs">{{ emp.cedula || '—' }}</td>
              <td class="table-td text-gray-600">{{ emp.position }}</td>
              <td class="table-td text-gray-600">{{ emp.phone || '—' }}</td>
              <td class="table-td text-right font-semibold">{{ fmt(emp.salary_base) }}</td>
              <td class="table-td text-gray-600">{{ emp.hire_date }}</td>
              <td class="table-td">
                <span :class="emp.active ? 'badge-green' : 'badge-red'">
                  {{ emp.active ? 'Activo' : 'Inactivo' }}
                </span>
              </td>
              <td class="table-td">
                <div class="flex gap-2">
                  <button class="text-blue-600 hover:text-blue-800 text-sm font-medium"
                          @click="openEdit(emp)">Editar</button>
                  <button class="text-red-500 hover:text-red-700 text-sm font-medium"
                          @click="confirmDelete(emp)">Eliminar</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal empleado -->
    <EmployeeModal v-model="showModal" :employee="selected"
                   @saved="store.fetchAll()" />

    <!-- Modal confirmar eliminar -->
    <BaseModal v-model="showDelete" title="Confirmar eliminación" size="sm">
      <p class="text-sm text-gray-600">
        ¿Seguro que deseas eliminar a
        <strong>{{ selected?.name }}</strong>?
        El empleado quedará inactivo.
      </p>
      <AlertMessage :message="deleteError" type="error" class="mt-3" />
      <template #footer>
        <button class="btn-secondary" @click="showDelete = false">Cancelar</button>
        <button class="btn-danger" :disabled="deleteLoading" @click="doDelete">
          Eliminar
        </button>
      </template>
    </BaseModal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AlertMessage   from '@/components/ui/AlertMessage.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import BaseModal      from '@/components/ui/BaseModal.vue'
import EmployeeModal  from '@/components/employees/EmployeeModal.vue'
import { useEmployeesStore } from '@/stores/employees'

const store         = useEmployeesStore()
const showModal     = ref(false)
const showDelete    = ref(false)
const selected      = ref(null)
const deleteError   = ref('')
const deleteLoading = ref(false)

const fmt = (n) =>
  new Intl.NumberFormat('es-NI', { style: 'currency', currency: 'NIO' }).format(n)

function openCreate()    { selected.value = null;        showModal.value  = true }
function openEdit(emp)   { selected.value = { ...emp };  showModal.value  = true }
function confirmDelete(emp) {
  selected.value    = emp
  deleteError.value = ''
  showDelete.value  = true
}

async function doDelete() {
  deleteLoading.value = true
  deleteError.value   = ''
  try {
    await store.remove(selected.value.id)
    showDelete.value = false
  } catch (e) {
    deleteError.value = e.message
  } finally {
    deleteLoading.value = false
  }
}

onMounted(() => store.fetchAll())
</script>