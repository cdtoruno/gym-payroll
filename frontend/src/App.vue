<template>
  <div class="min-h-screen flex bg-gray-50">

    <!-- Sidebar -->
    <aside class="w-60 bg-white border-r border-gray-200 flex flex-col fixed inset-y-0 left-0 z-20">
      <!-- Logo -->
      <div class="h-16 flex items-center gap-3 px-5 border-b border-gray-100">
        <div class="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center flex-shrink-0">
          <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
          </svg>
        </div>
        <div>
          <p class="text-sm font-bold text-gray-900 leading-none">Gym Payroll</p>
          <p class="text-xs text-gray-400 mt-0.5">Sistema de nómina</p>
        </div>
      </div>

      <!-- Nav -->
      <nav class="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        <RouterLink v-for="item in navItems" :key="item.to" :to="item.to"
          class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors"
          :class="isActive(item.to)
            ? 'bg-blue-50 text-blue-700'
            : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'">
          <svg class="w-5 h-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="item.icon"/>
          </svg>
          {{ item.label }}
        </RouterLink>
      </nav>

      <!-- Footer -->
      <div class="px-5 py-4 border-t border-gray-100">
        <p class="text-xs text-gray-400">Gym Dado — v1.0.0</p>
      </div>
    </aside>

    <!-- Main -->
    <div class="flex-1 ml-60 flex flex-col min-h-screen">
      <!-- Top bar -->
      <header class="h-16 bg-white border-b border-gray-200 flex items-center px-8 sticky top-0 z-10">
        <h2 class="text-sm font-semibold text-gray-500">{{ currentTitle }}</h2>
      </header>

      <!-- Page -->
      <main class="flex-1 px-8 py-6">
        <RouterView v-slot="{ Component }">
          <KeepAlive :include="['PayrollView']">
            <component :is="Component" />
          </KeepAlive>
        </RouterView>
      </main>
    </div>

  </div>
</template>

<script setup>
import { computed } from 'vue'
import { RouterLink, RouterView, useRoute } from 'vue-router'

const route = useRoute()

const currentTitle = computed(() => ({
  '/dashboard':       'Dashboard',
  '/employees':       'Empleados',
  '/vacations':       'Vacaciones',
  '/payroll':         'Generar Nómina',
  '/payroll/history': 'Historial de Nómina'
}[route.path] || 'Gym Payroll'))

const isActive = (path) =>
  route.path === path

const navItems = [
  {
    to: '/dashboard',
    label: 'Dashboard',
    icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6'
  },
  {
    to: '/employees',
    label: 'Empleados',
    icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z'
  },
  {
    to: '/vacations',
    label: 'Vacaciones',
    icon: 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z'
  },
  {
    to: '/payroll',
    label: 'Generar Nómina',
    icon: 'M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1'
  },
  {
    to: '/payroll/history',
    label: 'Historial',
    icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2'
  },
]
</script>