<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-2xl font-bold text-gray-900">Vacaciones</h1>
      <p class="text-sm text-gray-500 mt-1">Gestión de faltas por empleado</p>
    </div>

    <!-- Filtro de mes -->
    <div class="card py-4">
      <div class="flex flex-wrap gap-4 items-end">
        <div>
          <label class="label">Mes</label>
          <select v-model="filtroMes" class="input w-40">
            <option v-for="m in meses" :key="m.value" :value="m.value">
              {{ m.label }}
            </option>
          </select>
        </div>
        <div>
          <label class="label">Año</label>
          <select v-model="filtroAnio" class="input w-32">
            <option v-for="y in anios" :key="y" :value="y">{{ y }}</option>
          </select>
        </div>
        <div class="pb-2">
          <span class="text-sm text-gray-500">
            Mostrando faltas de
            <strong class="text-gray-800">{{ mesLabelCompleto }}</strong>
          </span>
        </div>
      </div>
    </div>

    <AlertMessage :message="globalError" type="error" />

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">

      <!-- ── Lista de empleados ─────────────────────────────────────────── -->
      <div>
        <h2 class="text-base font-semibold text-gray-900 mb-3">
          Empleados
          <span class="text-sm font-normal text-gray-400 ml-1">
            ({{ empStore.activeEmployees.length }} activos)
          </span>
        </h2>

        <!-- Leyenda -->
        <div class="flex gap-4 mb-3 text-xs text-gray-500">
          <span class="flex items-center gap-1">
            <span class="w-2.5 h-2.5 rounded-full bg-green-100
                         border border-green-300 inline-block"></span>
            0 faltas
          </span>
          <span class="flex items-center gap-1">
            <span class="w-2.5 h-2.5 rounded-full bg-yellow-100
                         border border-yellow-300 inline-block"></span>
            1 falta
          </span>
          <span class="flex items-center gap-1">
            <span class="w-2.5 h-2.5 rounded-full bg-red-100
                         border border-red-300 inline-block"></span>
            2+ faltas
          </span>
        </div>

        <LoadingSpinner v-if="empStore.loading" />

        <div v-else class="card p-0 overflow-hidden divide-y divide-gray-50">
          <div v-for="emp in empStore.activeEmployees" :key="emp.id"
               class="flex items-center gap-3 px-5 py-4
                      hover:bg-gray-50 transition-colors">

            <!-- Avatar -->
            <div class="w-9 h-9 rounded-full flex items-center justify-center
                        text-sm font-semibold flex-shrink-0"
                 :style="avatarStyle(emp.name)">
              {{ initials(emp.name) }}
            </div>

            <!-- Nombre y cargo -->
            <div class="flex-1 min-w-0">
              <p class="font-semibold text-gray-900 text-sm truncate">
                {{ emp.name }}
              </p>
              <p class="text-xs text-gray-400">{{ emp.position }}</p>
            </div>

            <!-- Contador de faltas — ancho fijo siempre -->
            <div class="flex flex-col items-center flex-shrink-0 w-16">
              <span class="text-xs text-gray-400 mb-0.5">Faltas</span>
              <div class="w-9 h-9 rounded-full flex items-center justify-center
                          text-sm font-bold border flex-shrink-0"
                   :class="faltasClase(faltasDelMes(emp.id))">
                {{ faltasDelMes(emp.id) }}
              </div>
            </div>

            <!-- Botón fijo sin badge interno -->
            <button
              class="flex-shrink-0 text-xs font-medium w-20 py-1.5
                     rounded-lg border transition-colors text-center
                     border-blue-200 text-blue-600 hover:bg-blue-50"
              :title="`${faltasDelMes(emp.id)} falta(s) registrada(s) este mes`"
              @click="abrirRegistroFalta(emp)">
              + Falta
            </button>
          </div>
        </div>
      </div>

      <!-- ── Historial del mes ───────────────────────────────────────────── -->
      <div>
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-base font-semibold text-gray-900">
            Historial de faltas
          </h2>
          <span class="text-xs text-gray-400">
            {{ absences.length }} falta(s) en {{ mesLabelCompleto }}
          </span>
        </div>

        <!-- Filtro por empleado -->
        <div class="mb-3">
          <select v-model="filtroEmpleado" class="input text-sm w-full">
            <option value="">Todos los empleados</option>
            <option v-for="e in empStore.activeEmployees"
                    :key="e.id" :value="e.id">
              {{ e.name }}
            </option>
          </select>
        </div>

        <LoadingSpinner v-if="loadingAbsences" />

        <div v-else-if="!absencesFiltradas.length"
             class="card text-center py-10 text-gray-400 text-sm">
          No hay faltas registradas en {{ mesLabelCompleto }}.
        </div>

        <div v-else class="space-y-2">
          <div v-for="a in absencesFiltradas" :key="a.id"
               class="card py-3 px-4 flex items-center gap-3">

            <!-- Círculo con día y mes abreviado -->
            <div class="w-12 h-12 rounded-full flex flex-col items-center
                        justify-center flex-shrink-0 border"
                 :class="a.es_q1
                   ? 'bg-red-50 border-red-200 text-red-700'
                   : 'bg-yellow-50 border-yellow-200 text-yellow-700'">
              <span class="text-base font-bold leading-none">
                {{ diaFecha(a.fecha) }}
              </span>
              <span class="text-xs leading-none mt-0.5 opacity-70">
                {{ mesCorto(a.fecha) }}
              </span>
            </div>

            <!-- Detalle -->
            <div class="flex-1 min-w-0">
              <p class="font-semibold text-gray-900 text-sm">
                {{ a.employee_name }}
              </p>
              <p class="text-xs text-gray-700 mt-0.5 font-medium">
                {{ fechaCompleta(a.fecha) }}
              </p>
              <div class="flex items-center gap-2 mt-1 flex-wrap">
                <span class="badge text-xs"
                      :class="a.es_q1 ? 'badge-blue' : 'badge-yellow'">
                  {{ a.quincena_label }}
                </span>
                <span class="text-xs text-gray-400">
                  Afecta:
                  <strong class="text-gray-600">
                    {{ a.mes_afectado_str }}
                  </strong>
                  <span class="italic ml-1">
                    ({{ a.es_q1 ? 'mismo mes' : 'mes siguiente' }})
                  </span>
                </span>
              </div>
              <p v-if="a.motivo && a.motivo !== 'Falta por vacaciones'"
                 class="text-xs text-gray-400 mt-0.5 italic">
                {{ a.motivo }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ── Modal registrar falta ─────────────────────────────────────────── -->
    <BaseModal v-model="showFalta"
               :title="`Registrar falta — ${faltaEmpleado?.name}`"
               size="sm">
      <div class="space-y-4">
        <AlertMessage :message="faltaError"   type="error"   />
        <AlertMessage :message="faltaSuccess" type="success" />

        <!-- Info contexto -->
        <div class="rounded-lg bg-blue-50 border border-blue-100 p-3 text-sm">
          <p class="text-blue-700 font-medium">
            Registrando falta para
            <strong>{{ mesLabelCompleto }}</strong>
          </p>
          <p class="text-blue-500 text-xs mt-0.5">
            Faltas registradas este mes:
            <strong>
              {{ faltaEmpleado ? faltasDelMes(faltaEmpleado.id) : 0 }}
            </strong>
          </p>
        </div>

        <!-- Fecha — limitada al mes del filtro -->
        <div>
          <label class="label">Día de la falta *</label>
          <input v-model="faltaForm.fecha" class="input" type="date"
                 :min="fechaMinMes" :max="fechaMaxMes" required />

          <!-- Indicador Q1/Q2 + impacto -->
          <div v-if="faltaForm.fecha && !faltaError"
               class="mt-2 rounded-lg p-3 text-sm border"
               :class="esFaltaQ1
                 ? 'bg-blue-50 border-blue-200 text-blue-800'
                 : 'bg-yellow-50 border-yellow-200 text-yellow-800'">
            <div class="font-semibold">
              {{ esFaltaQ1
                ? 'Falta en Q1 (días 1–15)'
                : 'Falta en Q2 (días 16–31)' }}
            </div>
            <div class="text-xs mt-1">
              {{ esFaltaQ1
                ? `Descuenta de la nómina de ${mesLabelCompleto}`
                : `Descuenta del Q1 de ${mesLabelSiguiente}` }}
            </div>
            <div class="mt-2 pt-2 border-t border-current border-opacity-20
                        flex justify-between font-medium text-xs">
              <span>Monto Q1 afectado</span>
              <span>{{ fmt(montoTrasRegistro) }}</span>
            </div>
          </div>
        </div>

        <!-- Motivo -->
        <div>
          <label class="label">Motivo (opcional)</label>
          <input v-model="faltaForm.motivo" class="input" type="text"
                 placeholder="Falta por vacaciones" />
        </div>

        <!-- Nómina actualizada -->
        <div v-if="nominaActualizada"
             class="rounded-lg bg-purple-50 border border-purple-200 p-3 text-sm">
          <p class="font-semibold text-purple-700 mb-1">
            Nómina Q1 ajustada automáticamente
          </p>
          <div class="grid grid-cols-2 gap-y-1 text-purple-800 text-xs">
            <span>Vacaciones</span>
            <span class="text-right">
              {{ fmt(nominaActualizada.vacation_payment) }}
            </span>
            <span>Nuevo total</span>
            <span class="text-right font-bold">
              {{ fmt(nominaActualizada.total) }}
            </span>
          </div>
        </div>
      </div>

      <template #footer>
        <button class="btn-secondary" @click="showFalta = false">Cancelar</button>
        <button class="btn-primary"
                :disabled="savingFalta || !faltaForm.fecha || !!faltaError"
                @click="confirmarFalta">
          <svg v-if="savingFalta" class="animate-spin h-4 w-4"
               fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10"
                    stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
          </svg>
          Confirmar falta
        </button>
      </template>
    </BaseModal>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import AlertMessage   from '@/components/ui/AlertMessage.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import BaseModal      from '@/components/ui/BaseModal.vue'
import { useEmployeesStore } from '@/stores/employees'
import { useVacationsStore  } from '@/stores/vacations'
import api from '@/services/api'

const empStore = useEmployeesStore()
const vacStore = useVacationsStore()

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
  const y = new Date().getFullYear()
  return [y, y - 1, y - 2]
})

// ── Filtro principal ──────────────────────────────────────────────────────────
const filtroMes      = ref(new Date().getMonth() + 1)
const filtroAnio     = ref(new Date().getFullYear())
const filtroEmpleado = ref('')

const mesLabelCompleto = computed(() => {
  const m = meses.find(x => x.value === filtroMes.value)
  return m ? `${m.label} ${filtroAnio.value}` : ''
})

// ── Fechas límite del mes para el date input ──────────────────────────────────
const fechaMinMes = computed(() => {
  const m = String(filtroMes.value).padStart(2, '0')
  return `${filtroAnio.value}-${m}-01`
})

const fechaMaxMes = computed(() => {
  const lastDay = new Date(filtroAnio.value, filtroMes.value, 0).getDate()
  const m       = String(filtroMes.value).padStart(2, '0')
  return `${filtroAnio.value}-${m}-${lastDay}`
})

// ── Historial de faltas ───────────────────────────────────────────────────────
const absences        = ref([])
const loadingAbsences = ref(false)
const globalError     = ref('')

async function fetchAbsences() {
  loadingAbsences.value = true
  globalError.value     = ''
  try {
    const res = await api.get('/vacations/absences/', {
      params: { month: filtroMes.value, year: filtroAnio.value }
    })
    absences.value = res.data.results ?? res.data
  } catch (e) {
    globalError.value = e.message
  } finally {
    loadingAbsences.value = false
  }
}

// Filtro por empleado en historial (solo frontend)
const absencesFiltradas = computed(() => {
  if (!filtroEmpleado.value) return absences.value
  return absences.value.filter(a => a.employee === filtroEmpleado.value)
})

// Número de faltas del mes por empleado
const faltasDelMes = (employeeId) =>
  absences.value.filter(a => a.employee === employeeId).length

// Recargar al cambiar mes o año
watch([filtroMes, filtroAnio], fetchAbsences)

// ── Formateo ──────────────────────────────────────────────────────────────────
const fmt = (n) =>
  new Intl.NumberFormat('es-NI', {
    style: 'currency', currency: 'NIO'
  }).format(n || 0)

const diaFecha = (dateStr) =>
  new Date(dateStr + 'T00:00:00').getDate()

const mesCorto = (dateStr) => {
  const mes = meses.find(
    m => m.value === new Date(dateStr + 'T00:00:00').getMonth() + 1
  )
  return mes?.label.slice(0, 3) || ''
}

const fechaCompleta = (dateStr) => {
  if (!dateStr) return ''
  const d   = new Date(dateStr + 'T00:00:00')
  const mes = meses.find(m => m.value === d.getMonth() + 1)
  return `${d.getDate()} de ${mes?.label} ${d.getFullYear()}`
}

const mesLabelSiguiente = computed(() => {
  const next = new Date(filtroAnio.value, filtroMes.value, 1)
  const mes  = meses.find(m => m.value === next.getMonth() + 1)
  return `${mes?.label} ${next.getFullYear()}`
})

// ── Helpers visuales ──────────────────────────────────────────────────────────
const avatarColors = [
  { bg: '#E6F1FB', color: '#0C447C' },
  { bg: '#EAF3DE', color: '#27500A' },
  { bg: '#FAEEDA', color: '#633806' },
  { bg: '#EEEDFE', color: '#3C3489' },
  { bg: '#E1F5EE', color: '#085041' },
]

const initials = (name) =>
  name
    ? name.split(' ').slice(0, 2).map(w => w[0]).join('').toUpperCase()
    : '?'

const avatarStyle = (name) => {
  const idx    = (name?.charCodeAt(0) || 0) % avatarColors.length
  const colors = avatarColors[idx]
  return `background:${colors.bg};color:${colors.color}`
}

const faltasClase = (faltas) => {
  if (faltas === 0) return 'bg-green-50 border-green-300 text-green-700'
  if (faltas === 1) return 'bg-yellow-50 border-yellow-300 text-yellow-700'
  return 'bg-red-50 border-red-300 text-red-600'
}

// ── Modal registrar falta ─────────────────────────────────────────────────────
const showFalta         = ref(false)
const faltaEmpleado     = ref(null)
const faltaError        = ref('')
const faltaSuccess      = ref('')
const savingFalta       = ref(false)
const nominaActualizada = ref(null)

const faltaForm = ref({ fecha: '', motivo: '' })

const esFaltaQ1 = computed(() => {
  if (!faltaForm.value.fecha) return false
  return new Date(faltaForm.value.fecha + 'T00:00:00').getDate() <= 15
})

const montoTrasRegistro = computed(() => {
  if (!faltaEmpleado.value || !faltaForm.value.fecha) return 0
  const salary     = parseFloat(faltaEmpleado.value.salary_base || 0)
  const vac        = vacStore.vacations.find(
    v => v.employee === faltaEmpleado.value.id
  )
  const diasActual = vac ? vac.dias_a_pagar : 2
  if (!esFaltaQ1.value) return (salary / 12) * diasActual
  return (salary / 12) * Math.max(0, diasActual - 1)
})

// Validar duplicado al seleccionar fecha
watch(() => faltaForm.value.fecha, (fecha) => {
  if (!fecha || !faltaEmpleado.value) return
  const yaExiste = absences.value.some(
    a => a.employee === faltaEmpleado.value.id && a.fecha === fecha
  )
  if (yaExiste) {
    faltaError.value = (
      `${faltaEmpleado.value.name} ya tiene una falta registrada ` +
      `el ${fechaCompleta(fecha)}.`
    )
  } else {
    faltaError.value = ''
  }
})

function abrirRegistroFalta(emp) {
  faltaEmpleado.value     = emp
  faltaForm.value         = { fecha: fechaMinMes.value, motivo: '' }
  faltaError.value        = ''
  faltaSuccess.value      = ''
  nominaActualizada.value = null
  showFalta.value         = true
}

async function confirmarFalta() {
  if (!faltaForm.value.fecha) {
    faltaError.value = 'Selecciona el día.'
    return
  }

  faltaError.value        = ''
  faltaSuccess.value      = ''
  nominaActualizada.value = null
  savingFalta.value       = true

  try {
    const res = await api.post('/vacations/falta/', {
      employee_id: faltaEmpleado.value.id,
      fecha:       faltaForm.value.fecha,
      motivo:      faltaForm.value.motivo || 'Falta por vacaciones',
    })

    faltaSuccess.value = res.data.message

    if (res.data.nomina_actualizada) {
      nominaActualizada.value = res.data.nomina_actualizada
    }

    await vacStore.fetchAll()
    await fetchAbsences()
    setTimeout(() => { showFalta.value = false }, 2000)
  } catch (e) {
    faltaError.value = e.message
  } finally {
    savingFalta.value = false
  }
}

onMounted(async () => {
  if (!empStore.employees.length) await empStore.fetchAll()
  await vacStore.fetchAll()
  await fetchAbsences()
})
</script>