<template>
  <BaseModal v-model="show" :title="isEdit ? 'Editar empleado' : 'Nuevo empleado'" size="md">
    <form @submit.prevent="submit" class="space-y-4">
      <AlertMessage :message="error" type="error" />

      <div class="grid grid-cols-2 gap-4">
        <!-- Nombre -->
        <div class="col-span-2">
          <label class="label">Nombre completo *</label>
          <input v-model="form.name" class="input" type="text"
                 placeholder="Juan García" required />
        </div>

        <!-- Cédula -->
        <div>
          <label class="label">Cédula</label>
          <input v-model="form.cedula" class="input" type="text"
                 placeholder="001-000000-0000X" />
        </div>

        <!-- Teléfono -->
        <div>
          <label class="label">Teléfono</label>
          <input v-model="form.phone" class="input" type="tel"
                 placeholder="8888-0000" />
        </div>

        <!-- Cargo -->
        <div class="col-span-2">
          <label class="label">Cargo *</label>
          <input v-model="form.position" class="input" type="text"
                 placeholder="Entrenador" required />
        </div>

        <!-- Salario -->
        <div>
          <label class="label">Salario base quincenal *</label>
          <div class="relative">
            <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm">C$</span>
            <input v-model="form.salary_base" class="input pl-9" type="number"
                   min="0" step="0.01" placeholder="0.00" required />
          </div>
        </div>

        <!-- Fecha contratación -->
        <div>
          <label class="label">Fecha de contratación *</label>
          <input v-model="form.hire_date" class="input" type="date" required />
        </div>

        <!-- Separador horario -->
        <div class="col-span-2 border-t border-gray-100 pt-3">
          <p class="text-sm font-semibold text-gray-700 mb-3">Horario de trabajo</p>
          <div class="grid grid-cols-3 gap-3">
            <!-- Hora entrada -->
            <div>
              <label class="label">Hora de entrada</label>
              <input v-model="form.hora_entrada" class="input" type="time" />
            </div>

            <!-- Hora salida -->
            <div>
              <label class="label">Hora de salida</label>
              <input v-model="form.hora_salida" class="input" type="time" />
            </div>

            <!-- Horas por día -->
            <div>
              <label class="label">Horas por día</label>
              <input v-model="form.horas_por_dia" class="input" type="number"
                     min="1" max="24" step="0.5" placeholder="8" />
            </div>
          </div>

          <!-- Preview valor por hora -->
          <div v-if="valorPorHora > 0"
               class="mt-2 text-xs text-gray-500 bg-gray-50 rounded-lg px-3 py-2">
            Valor por hora:
            <strong class="text-gray-700">{{ fmt(valorPorHora) }}</strong>
            <span class="ml-2 text-gray-400">
              (C${{ form.salary_base }} ÷ 15 ÷ {{ form.horas_por_dia }} hrs)
            </span>
          </div>
        </div>

        <!-- Activo -->
        <div class="col-span-2 flex items-center gap-3">
          <input v-model="form.active" id="active" type="checkbox"
                 class="w-4 h-4 text-blue-600 rounded border-gray-300
                        focus:ring-blue-500" />
          <label for="active" class="text-sm font-medium text-gray-700">
            Empleado activo
          </label>
        </div>
      </div>
    </form>

    <template #footer>
      <button type="button" class="btn-secondary" @click="show = false">
        Cancelar
      </button>
      <button type="button" class="btn-primary" :disabled="loading" @click="submit">
        <svg v-if="loading" class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10"
                  stroke="currentColor" stroke-width="4"/>
          <path class="opacity-75" fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
        </svg>
        {{ isEdit ? 'Guardar cambios' : 'Crear empleado' }}
      </button>
    </template>
  </BaseModal>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import BaseModal    from '@/components/ui/BaseModal.vue'
import AlertMessage from '@/components/ui/AlertMessage.vue'
import { useEmployeesStore } from '@/stores/employees'

const props = defineProps({
  modelValue: Boolean,
  employee:   { type: Object, default: null }
})
const emit = defineEmits(['update:modelValue', 'saved'])

const store   = useEmployeesStore()
const loading = ref(false)
const error   = ref('')
const isEdit  = computed(() => !!props.employee?.id)

const emptyForm = () => ({
  name: '', cedula: '', phone: '', position: '',
  salary_base: '', hire_date: '', active: true,
  hora_entrada: '', hora_salida: '', horas_por_dia: ''
})

const form = ref(emptyForm())

const show = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v)
})

const valorPorHora = computed(() => {
  if (!form.value.salary_base || !form.value.horas_por_dia) return 0
  return parseFloat(form.value.salary_base) / 15 / parseFloat(form.value.horas_por_dia)
})

const fmt = (n) =>
  new Intl.NumberFormat('es-NI', { style: 'currency', currency: 'NIO' }).format(n || 0)

watch(() => props.employee, (emp) => {
  form.value  = emp ? { ...emp } : emptyForm()
  error.value = ''
}, { immediate: true })

async function submit() {
  error.value   = ''
  loading.value = true
  try {
    let saved
    if (isEdit.value) {
      saved = await store.update(props.employee.id, form.value)
    } else {
      saved = await store.create(form.value)
    }
    emit('saved', saved)
    show.value = false
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>