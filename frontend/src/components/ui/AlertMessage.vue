<template>
  <Transition name="fade">
    <div v-if="message"
         class="flex items-start gap-3 px-4 py-3 rounded-lg text-sm font-medium"
         :class="classes">
      <svg class="w-5 h-5 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path v-if="type === 'error'"
              stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
        <path v-else-if="type === 'success'"
              stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
        <path v-else
              stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
      </svg>
      <span>{{ message }}</span>
    </div>
  </Transition>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  message: String,
  type:    { type: String, default: 'error' }
})

const classes = computed(() => ({
  error:   'bg-red-50 text-red-700 border border-red-200',
  success: 'bg-green-50 text-green-700 border border-green-200',
  info:    'bg-blue-50 text-blue-700 border border-blue-200'
}[props.type]))
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from,  .fade-leave-to      { opacity: 0; }
</style>