<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-2xl font-bold text-gray-900">Generar Nómina</h1>
      <p class="text-sm text-gray-500 mt-1">
        Calcula y registra el pago quincenal de cada empleado
      </p>
    </div>

    <!-- Selector de fecha y período -->
    <div class="card py-4">
      <div class="flex flex-wrap gap-4 items-end">
        <div>
          <label class="label">Fecha *</label>
          <input v-model="fecha" class="input w-44" type="date"
                 @change="onFechaPeriodoChange" />
        </div>
        <div>
          <label class="label">Período *</label>
          <select v-model="period" class="input w-56"
                  @change="onFechaPeriodoChange">
            <option value="">— Selecciona —</option>
            <option :value="1">Primera quincena (1–15)</option>
            <option :value="2">Segunda quincena (16–fin)</option>
          </select>
        </div>
        <div v-if="fecha && period" class="text-sm text-gray-500 pb-2 flex gap-2">
          <span class="badge badge-blue">{{ registros.length }} generadas</span>
          <span class="badge badge-green">
            {{ empStore.activeEmployees.length - registros.length }} pendientes
          </span>
          <button class="text-xs text-red-400 hover:text-red-600 underline ml-2"
                  @click="limpiarTodo">
            Limpiar sesión
          </button>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">

      <!-- ── Columna izquierda: formulario ─────────────────────────────── -->
      <div class="card space-y-5">
        <h2 class="text-lg font-semibold text-gray-900">
          {{ editando ? 'Editar nómina' : 'Agregar empleado' }}
        </h2>

        <AlertMessage :message="formError"   type="error"   />
        <AlertMessage :message="formSuccess" type="success" />

        <div class="grid grid-cols-2 gap-4">
          <!-- Empleado -->
          <div class="col-span-2">
            <label class="label">Empleado *</label>
            <select v-model="form.employee" class="input" required
                    :disabled="!!editando">
              <option value="">— Selecciona un empleado —</option>
              <option v-for="e in empStore.activeEmployees" :key="e.id"
                      :value="e.id"
                      :disabled="yaAgregado(e.id) && !editando">
                {{ yaAgregado(e.id) && !editando ? '✓' : '' }}
                {{ e.name }} — {{ e.position }}
                {{ yaAgregado(e.id) && !editando ? '(ya generada)' : '' }}
              </option>
            </select>
          </div>

          <!-- Viático -->
          <div>
            <label class="label">Viático</label>
            <div class="relative">
              <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm">C$</span>
              <input v-model="form.viatico" class="input pl-9" type="number"
                     min="0" step="0.01" placeholder="0.00"
                     @input="actualizarPreview" />
            </div>
          </div>

          <!-- Otras deducciones -->
          <div>
            <label class="label">Otras deducciones</label>
            <div class="relative">
              <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm">C$</span>
              <input v-model="form.otras_deducciones" class="input pl-9" type="number"
                     min="0" step="0.01" placeholder="0.00"
                     @input="actualizarPreview" />
            </div>
          </div>

          <!-- Préstamo -->
          <div>
            <label class="label">Préstamo / Adelanto</label>
            <div class="relative">
              <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm">C$</span>
              <input v-model="form.prestamo_adelanto" class="input pl-9" type="number"
                     min="0" step="0.01" placeholder="0.00"
                     @input="actualizarPreview" />
            </div>
          </div>

          <!-- Notas -->
          <div>
            <label class="label">Notas</label>
            <input v-model="form.notes" class="input" type="text"
                   placeholder="Opcional…"
                   @input="persistirForm" />
          </div>
        </div>

        <!-- Vista previa -->
        <div v-if="form.employee && preview.salary_base"
             class="rounded-xl bg-blue-50 border border-blue-100 p-4">
          <p class="text-xs font-semibold text-blue-600 uppercase tracking-wider mb-3">
            Vista previa del cálculo
          </p>
          <div class="grid grid-cols-2 gap-y-2 text-sm">
            <span class="text-gray-600">Salario ordinario</span>
            <span class="text-right font-medium">{{ fmt(preview.salary_base) }}</span>

            <!-- Vacaciones solo en Q1 -->
            <template v-if="period == 1">
              <span class="text-gray-600">
                Vacaciones
                <span class="text-xs opacity-70">({{ preview.dias_a_pagar }} día(s))</span>
              </span>
              <span class="text-right font-medium"
                    :class="vacClass(preview.dias_a_pagar)">
                + {{ fmt(preview.vacation_payment) }}
              </span>
            </template>

            <span class="text-gray-600">Viático</span>
            <span class="text-right font-medium text-green-600">
              + {{ fmt(form.viatico || 0) }}
            </span>

            <span class="text-gray-600 font-medium">Sub-total</span>
            <span class="text-right font-semibold">{{ fmt(preview.sub_total) }}</span>

            <span class="text-gray-600">Otras deducciones</span>
            <span class="text-right text-red-500">
              − {{ fmt(form.otras_deducciones || 0) }}
            </span>

            <span class="text-gray-600">Préstamo / Adelanto</span>
            <span class="text-right text-red-500">
              − {{ fmt(form.prestamo_adelanto || 0) }}
            </span>

            <!-- Descuento por faltas solo en Q2 -->
            <template v-if="period == 2 && preview.descuento_faltas > 0">
              <span class="text-gray-600">
                Desc. por faltas
                <span class="text-xs opacity-70">
                  ({{ preview.dias_descuento }} día(s) × salario÷15)
                </span>
              </span>
              <span class="text-right font-medium text-red-500">
                − {{ fmt(preview.descuento_faltas) }}
              </span>
            </template>

            <div class="col-span-2 border-t border-blue-200 pt-2 mt-1
                        flex justify-between">
              <span class="font-bold text-gray-900">Total devengado</span>
              <span class="font-bold text-xl text-blue-700">
                {{ fmt(preview.total) }}
              </span>
            </div>
          </div>
        </div>

        <!-- Botones -->
        <div class="flex gap-3">
          <button class="btn-primary flex-1 justify-center py-3"
                  :disabled="!isValid || saving"
                  @click="guardar">
            <svg v-if="saving" class="animate-spin h-4 w-4"
                 fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10"
                      stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
            </svg>
            {{ editando ? 'Guardar cambios' : 'Agregar a la planilla' }}
          </button>
          <button v-if="editando" class="btn-secondary"
                  @click="cancelarEdicion">
            Cancelar
          </button>
        </div>
      </div>

      <!-- ── Columna derecha: registros ────────────────────────────────── -->
      <div class="card p-0 overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
          <h2 class="text-base font-semibold text-gray-900">Planilla actual</h2>
          <span v-if="registros.length" class="text-sm font-bold text-blue-700">
            Total: {{ fmt(totalGeneral) }}
          </span>
        </div>

        <LoadingSpinner v-if="loadingRegistros" />

        <div v-else-if="!fecha || !period"
             class="text-center py-12 text-gray-400 text-sm">
          Selecciona fecha y período para ver la planilla.
        </div>

        <div v-else-if="!registros.length"
             class="text-center py-12 text-gray-400 text-sm">
          No hay empleados agregados aún.
        </div>

        <div v-else class="divide-y divide-gray-50">
          <div v-for="r in registros" :key="r.id"
               class="px-6 py-4 hover:bg-gray-50 transition-colors"
               :class="editando?.id === r.id
                 ? 'bg-blue-50 border-l-4 border-blue-500' : ''">
            <div class="flex items-start justify-between gap-4">
              <div class="flex-1 min-w-0">
                <p class="font-semibold text-gray-900 truncate">
                  {{ r.employee_name }}
                </p>
                <p class="text-xs text-gray-400">{{ r.employee_cedula }}</p>

                <!-- Alerta vacaciones desactualizadas -->
                <div v-if="tieneVacacionesDesactualizadas(r)"
                     class="mt-1 flex items-center gap-1 text-xs text-amber-600">
                  <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24"
                       stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round"
                          stroke-width="2"
                          d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                  </svg>
                  Vacaciones cambiaron — editar para actualizar
                </div>

                <div class="mt-2 grid grid-cols-2 gap-x-4 gap-y-1
                            text-xs text-gray-500">
                  <span>Salario:
                    <strong>{{ fmt(r.salary_base) }}</strong>
                  </span>
                  <span v-if="r.vacation_payment > 0">
                    Vacaciones:
                    <strong class="text-purple-600">
                      {{ fmt(r.vacation_payment) }}
                    </strong>
                  </span>
                  <span v-if="r.viatico > 0">
                    Viático:
                    <strong class="text-green-600">{{ fmt(r.viatico) }}</strong>
                  </span>
                  <span v-if="r.otras_deducciones > 0">
                    Dedu.:
                    <strong class="text-red-500">
                      {{ fmt(r.otras_deducciones) }}
                    </strong>
                  </span>
                  <span v-if="r.prestamo_adelanto > 0">
                    Préstamo:
                    <strong class="text-red-500">
                      {{ fmt(r.prestamo_adelanto) }}
                    </strong>
                  </span>
                  <span v-if="r.descuento_faltas > 0">
                    Desc. faltas:
                    <strong class="text-red-600">
                      {{ fmt(r.descuento_faltas) }}
                    </strong>
                  </span>
                </div>
              </div>

              <div class="flex flex-col items-end gap-2 flex-shrink-0">
                <span class="font-bold text-lg text-gray-900">
                  {{ fmt(r.total) }}
                </span>
                <div class="flex gap-2">
                  <button
                    class="text-blue-600 hover:text-blue-800 text-xs font-medium"
                    @click="iniciarEdicion(r)">
                    Editar
                  </button>
                  <button
                    class="text-red-500 hover:text-red-700 text-xs font-medium"
                    @click="confirmarEliminar(r)">
                    Borrar
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Total -->
          <div class="px-6 py-4 bg-gray-50 flex justify-between items-center">
            <span class="text-sm font-semibold text-gray-700">
              {{ registros.length }} empleados
            </span>
            <span class="font-bold text-blue-700 text-lg">
              {{ fmt(totalGeneral) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal confirmar borrar -->
    <BaseModal v-model="showDelete" title="Confirmar eliminación" size="sm">
      <p class="text-sm text-gray-600">
        ¿Eliminar la nómina de
        <strong>{{ registroAEliminar?.employee_name }}</strong>?
      </p>
      <AlertMessage :message="deleteError" type="error" class="mt-3" />
      <template #footer>
        <button class="btn-secondary" @click="showDelete = false">Cancelar</button>
        <button class="btn-danger" :disabled="deleting" @click="eliminar">
          Eliminar
        </button>
      </template>
    </BaseModal>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onActivated } from 'vue'
import AlertMessage   from '@/components/ui/AlertMessage.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import BaseModal      from '@/components/ui/BaseModal.vue'
import { useEmployeesStore } from '@/stores/employees'
import { usePayrollStore    } from '@/stores/payroll'
import { useVacationsStore  } from '@/stores/vacations'
import api from '@/services/api'

const empStore = useEmployeesStore()
const vacStore = useVacationsStore()
const store    = usePayrollStore()

// ── Estado restaurado desde sesión persistida ─────────────────────────────────
const fecha    = ref(store.session.fecha)
const period   = ref(store.session.period)
const form     = ref({ ...store.session.form })
const editando = ref(store.session.editando)

const registros        = ref([])
const loadingRegistros = ref(false)
const formError        = ref('')
const formSuccess      = ref('')
const saving           = ref(false)
const preview          = ref({})

const showDelete        = ref(false)
const registroAEliminar = ref(null)
const deleteError       = ref('')
const deleting          = ref(false)

const fmt = (n) =>
  new Intl.NumberFormat('es-NI', { style: 'currency', currency: 'NIO' }).format(n || 0)

const vacClass = (dias) => {
  if (dias === 2) return 'text-green-600 font-medium'
  if (dias === 1) return 'text-yellow-600 font-medium'
  return 'text-red-500 font-medium'
}

const isValid = computed(() =>
  form.value.employee && fecha.value && period.value
)

const totalGeneral = computed(() =>
  registros.value.reduce((a, r) => a + parseFloat(r.total || 0), 0)
)

const yaAgregado = (employeeId) =>
  registros.value.some(r => r.employee === employeeId)

// ── Detectar vacaciones desactualizadas ───────────────────────────────────────
function tieneVacacionesDesactualizadas(registro) {
  if (period.value != 1) return false
  const vac = vacStore.vacations.find(v => v.employee === registro.employee)
  if (!vac) return false
  const montoEsperado = parseFloat(vac.monto_vacaciones)
  const montoActual   = parseFloat(registro.vacation_payment)
  return Math.abs(montoEsperado - montoActual) > 0.01
}

// ── Persistir estado ──────────────────────────────────────────────────────────
function persistirForm() {
  store.guardarSesion({
    fecha:    fecha.value,
    period:   period.value,
    form:     { ...form.value },
    editando: editando.value,
  })
}

// ── Cargar registros ──────────────────────────────────────────────────────────
async function cargarRegistros() {
  if (!fecha.value || !period.value) return
  loadingRegistros.value = true
  try {
    const res = await api.get('/payroll/', {
      params: {
        date_from: fecha.value,
        date_to:   fecha.value,
        period:    period.value
      }
    })
    registros.value = res.data.results ?? res.data
  } catch (e) {
    formError.value = e.message
  } finally {
    loadingRegistros.value = false
  }
}

async function onFechaPeriodoChange() {
  persistirForm()
  await cargarRegistros()
  if (form.value.employee) await actualizarPreview()
}

// ── Auto-seleccionar período según fecha ──────────────────────────────────────
watch(() => fecha.value, (nuevaFecha) => {
  if (!nuevaFecha) return
  const dia    = new Date(nuevaFecha + 'T00:00:00').getDate()
  period.value = dia <= 15 ? 1 : 2
  persistirForm()
  if (form.value.employee) actualizarPreview()
})

// ── Preview en tiempo real ────────────────────────────────────────────────────
async function actualizarPreview() {
  if (!form.value.employee || !fecha.value || !period.value) return
  try {
    const res = await api.get('/payroll/preview/', {
      params: { date: fecha.value, period: period.value }
    })
    const emp = res.data.find(e => e.employee_id === form.value.employee)
    if (!emp) return

    const vac      = period.value == 1 ? parseFloat(emp.vacation_payment || 0) : 0
    const desc     = period.value == 2 ? parseFloat(emp.descuento_faltas  || 0) : 0
    const sub_total = parseFloat(emp.salary_base)
      + vac
      + parseFloat(form.value.viatico || 0)
    const total = sub_total
      - parseFloat(form.value.otras_deducciones || 0)
      - parseFloat(form.value.prestamo_adelanto  || 0)
      - desc

    preview.value = {
      salary_base:      emp.salary_base,
      vacation_payment: emp.vacation_payment,
      dias_a_pagar:     emp.dias_a_pagar,
      descuento_faltas: emp.descuento_faltas,
      dias_descuento:   emp.dias_descuento,
      sub_total,
      total,
    }
  } catch {}
}

// Watch empleado
watch(() => form.value.employee, () => {
  persistirForm()
  actualizarPreview()
})

// Watch montos
watch([
  () => form.value.viatico,
  () => form.value.otras_deducciones,
  () => form.value.prestamo_adelanto,
], () => {
  persistirForm()
  actualizarPreview()
})

// ── Guardar ───────────────────────────────────────────────────────────────────
async function guardar() {
  formError.value   = ''
  formSuccess.value = ''
  saving.value      = true

  try {
    await api.post('/payroll/generate/', {
      employee:          form.value.employee,
      date:              fecha.value,
      period:            period.value,
      dias_laborados:    15,
      viatico:           parseFloat(form.value.viatico           || 0),
      otras_deducciones: parseFloat(form.value.otras_deducciones || 0),
      prestamo_adelanto: parseFloat(form.value.prestamo_adelanto || 0),
      notes:             form.value.notes || '',
    })

    const empName = empStore.activeEmployees
      .find(e => e.id === form.value.employee)?.name
    formSuccess.value = `✅ Nómina de ${empName} guardada correctamente.`

    form.value    = store.sesionVacia().form
    preview.value = {}
    editando.value = null

    store.guardarSesion({
      fecha:    fecha.value,
      period:   period.value,
      form:     { ...form.value },
      editando: null,
    })

    await cargarRegistros()
    await store.fetchAll()
  } catch (e) {
    formError.value = e.message
  } finally {
    saving.value = false
  }
}

// ── Edición ───────────────────────────────────────────────────────────────────
function iniciarEdicion(r) {
  editando.value = r
  form.value = {
    employee:          r.employee,
    viatico:           parseFloat(r.viatico           || 0),
    otras_deducciones: parseFloat(r.otras_deducciones || 0),
    prestamo_adelanto: parseFloat(r.prestamo_adelanto || 0),
    notes:             r.notes || '',
  }
  formError.value   = ''
  formSuccess.value = ''
  persistirForm()
  actualizarPreview()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function cancelarEdicion() {
  editando.value = null
  form.value     = store.sesionVacia().form
  preview.value  = {}
  formError.value   = ''
  formSuccess.value = ''
  persistirForm()
}

// ── Eliminar ──────────────────────────────────────────────────────────────────
function confirmarEliminar(r) {
  registroAEliminar.value = r
  deleteError.value       = ''
  showDelete.value        = true
}

async function eliminar() {
  deleting.value    = true
  deleteError.value = ''
  try {
    await api.delete(`/payroll/${registroAEliminar.value.id}/`)
    showDelete.value = false
    await cargarRegistros()
    await store.fetchAll()
  } catch (e) {
    deleteError.value = e.message
  } finally {
    deleting.value = false
  }
}

// ── Limpiar sesión ────────────────────────────────────────────────────────────
function limpiarTodo() {
  store.limpiarSesion()
  fecha.value     = ''
  period.value    = ''
  form.value      = store.sesionVacia().form
  editando.value  = null
  preview.value   = {}
  registros.value = []
}

// ── Inicializar ───────────────────────────────────────────────────────────────
async function inicializar() {
  if (!empStore.employees.length) await empStore.fetchAll()
  if (!vacStore.vacations.length) await vacStore.fetchAll()

  if (fecha.value && period.value) {
    await cargarRegistros()
    if (form.value.employee) await actualizarPreview()
  }
}

onMounted(inicializar)

onActivated(async () => {
  await vacStore.fetchAll()
  if (fecha.value && period.value) {
    await cargarRegistros()
    if (form.value.employee) await actualizarPreview()
  }
})
</script>