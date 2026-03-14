import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: { title: 'Dashboard' }
  },
  {
    path: '/employees',
    name: 'Employees',
    component: () => import('@/views/EmployeesView.vue'),
    meta: { title: 'Empleados' }
  },
  {
    path: '/vacations',
    name: 'Vacations',
    component: () => import('@/views/VacationsView.vue'),
    meta: { title: 'Vacaciones' }
  },
  {
    path: '/payroll',
    name: 'Payroll',
    component: () => import('@/views/PayrollView.vue'),
    meta: { title: 'Generar Nómina' }
  },
  {
    path: '/payroll/history',
    name: 'PayrollHistory',
    component: () => import('@/views/PayrollHistoryView.vue'),
    meta: { title: 'Historial de Nómina' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.afterEach((to) => {
  document.title = to.meta.title
    ? `${to.meta.title} — Gym Payroll`
    : 'Gym Payroll'
})

export default router