<template>
    <div class="space-y-6">
        <div>
            <h1 class="text-2xl font-bold text-gray-900">Asistencia</h1>
            <p class="text-sm text-gray-500 mt-1">
                Registro de llegadas tarde por empleado
            </p>
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
                        Mostrando tardanzas de
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

                <LoadingSpinner v-if="empStore.loading" />

                <div v-else class="card p-0 overflow-hidden divide-y divide-gray-50">
                    <div v-for="emp in empStore.activeEmployees" :key="emp.id" class="flex items-center gap-3 px-5 py-4
                      hover:bg-gray-50 transition-colors">

                        <!-- Avatar -->
                        <div class="w-9 h-9 rounded-full flex items-center justify-center
                        text-sm font-semibold flex-shrink-0" :style="avatarStyle(emp.name)">
                            {{ initials(emp.name) }}
                        </div>

                        <!-- Info -->
                        <div class="flex-1 min-w-0">
                            <p class="font-semibold text-gray-900 text-sm truncate">
                                {{ emp.name }}
                            </p>
                            <p class="text-xs text-gray-400">
                                {{ emp.hora_entrada
                                    ? `${emp.hora_entrada} — ${emp.hora_salida}`
                                    : 'Sin horario configurado' }}
                            </p>
                        </div>

                        <!-- Contador tardanzas -->
                        <div class="flex flex-col items-center flex-shrink-0 w-20">
                            <span class="text-xs text-gray-400 mb-0.5">Tardanzas</span>
                            <div class="w-9 h-9 rounded-full flex items-center justify-center
                          text-sm font-bold border" :class="tardanzasClase(tardanzasDelMes(emp.id))">
                                {{ tardanzasDelMes(emp.id) }}
                            </div>
                        </div>

                        <!-- Descuento acumulado -->
                        <div class="flex flex-col items-center flex-shrink-0 w-24">
                            <span class="text-xs text-gray-400 mb-0.5">Descuento</span>
                            <span class="text-sm font-semibold"
                                :class="descuentoDelMes(emp.id) > 0 ? 'text-red-500' : 'text-gray-400'">
                                {{ fmt(descuentoDelMes(emp.id)) }}
                            </span>
                        </div>

                        <!-- Botón -->
                        <button class="flex-shrink-0 text-xs font-medium w-24 py-1.5
                     rounded-lg border transition-colors text-center" :class="!emp.hora_entrada
                        ? 'border-gray-200 text-gray-400 cursor-not-allowed bg-gray-50'
                        : 'border-red-200 text-red-600 hover:bg-red-50'" :disabled="!emp.hora_entrada"
                            :title="!emp.hora_entrada ? 'Configura el horario primero' : 'Registrar tardanza'"
                            @click="abrirRegistro(emp)">
                            + Tardanza
                        </button>
                    </div>
                </div>
            </div>

            <!-- ── Historial del mes ───────────────────────────────────────────── -->
            <div>
                <div class="flex items-center justify-between mb-3">
                    <h2 class="text-base font-semibold text-gray-900">
                        Historial de tardanzas
                    </h2>
                    <span class="text-xs text-gray-400">
                        {{ records.length }} registro(s) en {{ mesLabelCompleto }}
                    </span>
                </div>

                <!-- Filtro por empleado -->
                <div class="mb-3">
                    <select v-model="filtroEmpleado" class="input text-sm w-full">
                        <option value="">Todos los empleados</option>
                        <option v-for="e in empStore.activeEmployees" :key="e.id" :value="e.id">
                            {{ e.name }}
                        </option>
                    </select>
                </div>

                <LoadingSpinner v-if="loadingRecords" />

                <div v-else-if="!recordsFiltrados.length" class="card text-center py-10 text-gray-400 text-sm">
                    No hay tardanzas registradas en {{ mesLabelCompleto }}.
                </div>

                <div v-else class="space-y-2">
                    <div v-for="r in recordsFiltrados" :key="r.id" class="card py-3 px-4 flex items-center gap-3">

                        <!-- Círculo con día -->
                        <div class="w-12 h-12 rounded-full flex flex-col items-center
                        justify-center flex-shrink-0 border
                        bg-red-50 border-red-200 text-red-700">
                            <span class="text-base font-bold leading-none">
                                {{ new Date(r.fecha + 'T00:00:00').getDate() }}
                            </span>
                            <span class="text-xs leading-none mt-0.5 opacity-70">
                                {{ mesCorto(r.fecha) }}
                            </span>
                        </div>

                        <!-- Detalle -->
                        <div class="flex-1 min-w-0">
                            <p class="font-semibold text-gray-900 text-sm">
                                {{ r.employee_name }}
                            </p>
                            <p class="text-xs text-gray-700 mt-0.5">
                                {{ fechaCompleta(r.fecha) }}
                            </p>
                            <div class="flex items-center gap-2 mt-1 flex-wrap">
                                <span class="badge" :class="r.period === 1 ? 'badge-blue' : 'badge-yellow'">
                                    {{ r.period === 1 ? 'Q1 (1–15)' : 'Q2 (16–fin)' }}
                                </span>
                                <span class="text-xs text-gray-500">
                                    Llegó a las
                                    <strong class="text-gray-700">{{ r.hora_llegada }}</strong>
                                    —
                                    <strong class="text-red-500">{{ r.minutos_tarde }} min tarde</strong>
                                </span>
                            </div>
                            <p v-if="r.notas" class="text-xs text-gray-400 mt-0.5 italic">
                                {{ r.notas }}
                            </p>
                        </div>

                        <!-- Descuento -->
                        <div class="flex-shrink-0 text-right">
                            <span class="text-sm font-bold text-red-600">
                                − {{ fmt(r.descuento) }}
                            </span>
                            <p class="text-xs text-gray-400 mt-0.5">
                                {{ Math.ceil(r.minutos_tarde / 60) }} hora(s)
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- ── Modal registrar tardanza ──────────────────────────────────────── -->
        <BaseModal v-model="showModal" :title="`Registrar tardanza — ${empleadoSeleccionado?.name}`" size="sm">
            <div class="space-y-4">
                <AlertMessage :message="formError" type="error" />
                <AlertMessage :message="formSuccess" type="success" />

                <!-- Info del empleado -->
                <div class="rounded-lg bg-gray-50 border border-gray-200 p-3 text-sm">
                    <div class="flex justify-between">
                        <span class="text-gray-500">Hora de entrada</span>
                        <strong>{{ empleadoSeleccionado?.hora_entrada }}</strong>
                    </div>
                    <div class="flex justify-between mt-1">
                        <span class="text-gray-500">Valor por hora</span>
                        <strong class="text-red-600">
                            {{ fmt(empleadoSeleccionado?.valor_por_hora) }}
                        </strong>
                    </div>
                    <div class="flex justify-between mt-1">
                        <span class="text-gray-500">Tardanzas este mes</span>
                        <strong>
                            {{ empleadoSeleccionado
                                ? tardanzasDelMes(empleadoSeleccionado.id)
                            : 0 }}
                        </strong>
                    </div>
                </div>

                <!-- Fecha -->
                <div>
                    <label class="label">Fecha *</label>
                    <input v-model="form.fecha" class="input" type="date" :min="fechaMinMes" :max="fechaMaxMes"
                        required />
                    <p v-if="form.fecha" class="text-xs mt-1"
                        :class="periodoFecha === 1 ? 'text-blue-500' : 'text-yellow-600'">
                        {{ periodoFecha === 1
                            ? 'Q1 — descuenta de primera quincena'
                            : 'Q2 — descuenta de segunda quincena' }}
                    </p>
                </div>

                <!-- Hora de llegada -->
                <div>
                    <label class="label">Hora de llegada real *</label>
                    <input v-model="form.hora_llegada" class="input" type="time" required />

                    <!-- Preview del descuento -->
                    <div v-if="form.hora_llegada && empleadoSeleccionado" class="mt-2 rounded-lg p-3 text-sm border
                      bg-red-50 border-red-200 text-red-800">
                        <div class="font-semibold">
                            Descuento a aplicar
                        </div>
                        <div class="flex justify-between mt-1 text-xs">
                            <span>1 hora de trabajo</span>
                            <strong>− {{ fmt(empleadoSeleccionado.valor_por_hora) }}</strong>
                        </div>
                    </div>
                </div>

                <!-- Notas -->
                <div>
                    <label class="label">Notas (opcional)</label>
                    <input v-model="form.notas" class="input" type="text" placeholder="Tráfico, emergencia, etc." />
                </div>

                <!-- Nómina actualizada -->
                <div v-if="nominaActualizada" class="rounded-lg bg-purple-50 border border-purple-200 p-3 text-sm">
                    <p class="font-semibold text-purple-700 mb-1">
                        Nómina ajustada automáticamente
                    </p>
                    <div class="grid grid-cols-2 gap-y-1 text-purple-800 text-xs">
                        <span>Nuevas deducciones</span>
                        <span class="text-right">
                            {{ fmt(nominaActualizada.otras_deducciones) }}
                        </span>
                        <span>Nuevo total</span>
                        <span class="text-right font-bold">
                            {{ fmt(nominaActualizada.total) }}
                        </span>
                    </div>
                </div>
            </div>

            <template #footer>
                <button class="btn-secondary" @click="showModal = false">Cancelar</button>
                <button class="btn-danger" :disabled="saving || !form.fecha || !form.hora_llegada" @click="confirmar">
                    <svg v-if="saving" class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    Registrar tardanza
                </button>
            </template>
        </BaseModal>
    </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import AlertMessage from '@/components/ui/AlertMessage.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import { useEmployeesStore } from '@/stores/employees'
import { useAttendanceStore } from '@/stores/attendance'
import api from '@/services/api'

const empStore = useEmployeesStore()
const attStore = useAttendanceStore()

// ── Catálogos ─────────────────────────────────────────────────────────────────
const meses = [
    { value: 1, label: 'Enero' },
    { value: 2, label: 'Febrero' },
    { value: 3, label: 'Marzo' },
    { value: 4, label: 'Abril' },
    { value: 5, label: 'Mayo' },
    { value: 6, label: 'Junio' },
    { value: 7, label: 'Julio' },
    { value: 8, label: 'Agosto' },
    { value: 9, label: 'Septiembre' },
    { value: 10, label: 'Octubre' },
    { value: 11, label: 'Noviembre' },
    { value: 12, label: 'Diciembre' },
]

const anios = computed(() => {
    const y = new Date().getFullYear()
    return [y, y - 1, y - 2]
})

// ── Filtros ───────────────────────────────────────────────────────────────────
const filtroMes = ref(new Date().getMonth() + 1)
const filtroAnio = ref(new Date().getFullYear())
const filtroEmpleado = ref('')

const mesLabelCompleto = computed(() => {
    const m = meses.find(x => x.value === filtroMes.value)
    return m ? `${m.label} ${filtroAnio.value}` : ''
})

const fechaMinMes = computed(() => {
    const m = String(filtroMes.value).padStart(2, '0')
    return `${filtroAnio.value}-${m}-01`
})

const fechaMaxMes = computed(() => {
    const lastDay = new Date(filtroAnio.value, filtroMes.value, 0).getDate()
    const m = String(filtroMes.value).padStart(2, '0')
    return `${filtroAnio.value}-${m}-${lastDay}`
})

// ── Records ───────────────────────────────────────────────────────────────────
const records = ref([])
const loadingRecords = ref(false)
const globalError = ref('')

async function fetchRecords() {
    loadingRecords.value = true
    globalError.value = ''
    try {
        const res = await api.get('/attendance/', {
            params: { month: filtroMes.value, year: filtroAnio.value }
        })
        records.value = res.data.results ?? res.data
    } catch (e) {
        globalError.value = e.message
    } finally {
        loadingRecords.value = false
    }
}

const recordsFiltrados = computed(() => {
    if (!filtroEmpleado.value) return records.value
    return records.value.filter(r => r.employee === filtroEmpleado.value)
})

const tardanzasDelMes = (employeeId) =>
    records.value.filter(r => r.employee === employeeId).length

const descuentoDelMes = (employeeId) =>
    records.value
        .filter(r => r.employee === employeeId)
        .reduce((acc, r) => acc + parseFloat(r.descuento || 0), 0)

watch([filtroMes, filtroAnio], fetchRecords)

// ── Formateo ──────────────────────────────────────────────────────────────────
const fmt = (n) =>
    new Intl.NumberFormat('es-NI', { style: 'currency', currency: 'NIO' }).format(n || 0)

const mesCorto = (dateStr) => {
    const mes = meses.find(
        m => m.value === new Date(dateStr + 'T00:00:00').getMonth() + 1
    )
    return mes?.label.slice(0, 3) || ''
}

const fechaCompleta = (dateStr) => {
    if (!dateStr) return ''
    const d = new Date(dateStr + 'T00:00:00')
    const mes = meses.find(m => m.value === d.getMonth() + 1)
    return `${d.getDate()} de ${mes?.label} ${d.getFullYear()}`
}

// ── Helpers visuales ──────────────────────────────────────────────────────────
const avatarColors = [
    { bg: '#E6F1FB', color: '#0C447C' },
    { bg: '#EAF3DE', color: '#27500A' },
    { bg: '#FAEEDA', color: '#633806' },
    { bg: '#EEEDFE', color: '#3C3489' },
    { bg: '#E1F5EE', color: '#085041' },
]

const initials = (name) =>
    name ? name.split(' ').slice(0, 2).map(w => w[0]).join('').toUpperCase() : '?'

const avatarStyle = (name) => {
    const idx = (name?.charCodeAt(0) || 0) % avatarColors.length
    const colors = avatarColors[idx]
    return `background:${colors.bg};color:${colors.color}`
}

const tardanzasClase = (n) => {
    if (n === 0) return 'bg-green-50 border-green-300 text-green-700'
    if (n <= 2) return 'bg-yellow-50 border-yellow-300 text-yellow-700'
    return 'bg-red-50 border-red-300 text-red-600'
}

// ── Modal ─────────────────────────────────────────────────────────────────────
const showModal = ref(false)
const empleadoSeleccionado = ref(null)
const formError = ref('')
const formSuccess = ref('')
const saving = ref(false)
const nominaActualizada = ref(null)

const form = ref({ fecha: '', hora_llegada: '', notas: '' })

const periodoFecha = computed(() => {
    if (!form.value.fecha) return null
    return new Date(form.value.fecha + 'T00:00:00').getDate() <= 15 ? 1 : 2
})

function abrirRegistro(emp) {
    empleadoSeleccionado.value = emp
    form.value = {
        fecha: fechaMinMes.value,
        hora_llegada: '',
        notas: ''
    }
    formError.value = ''
    formSuccess.value = ''
    nominaActualizada.value = null
    showModal.value = true
}

async function confirmar() {
    formError.value = ''
    formSuccess.value = ''
    nominaActualizada.value = null
    saving.value = true

    try {
        const res = await api.post('/attendance/register/', {
            employee_id: empleadoSeleccionado.value.id,
            fecha: form.value.fecha,
            hora_llegada: form.value.hora_llegada,
            notas: form.value.notas,
        })

        formSuccess.value = res.data.message

        if (res.data.nomina_actualizada) {
            nominaActualizada.value = res.data.nomina_actualizada
        }

        await fetchRecords()
        setTimeout(() => { showModal.value = false }, 2000)
    } catch (e) {
        formError.value = e.message
    } finally {
        saving.value = false
    }
}

onMounted(async () => {
    if (!empStore.employees.length) await empStore.fetchAll()
    await fetchRecords()
})
</script>