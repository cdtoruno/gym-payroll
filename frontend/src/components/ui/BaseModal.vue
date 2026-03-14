<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="modelValue" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <!-- Backdrop -->
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm"
             @click="$emit('update:modelValue', false)" />
        <!-- Panel -->
        <div class="relative z-10 w-full bg-white rounded-2xl shadow-xl border border-gray-200 overflow-hidden"
             :class="sizeClass">
          <!-- Header -->
          <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100">
            <h3 class="text-lg font-semibold text-gray-900">{{ title }}</h3>
            <button @click="$emit('update:modelValue', false)"
                    class="text-gray-400 hover:text-gray-600 transition-colors p-1 rounded-lg hover:bg-gray-100">
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>
          <!-- Body -->
          <div class="px-6 py-5">
            <slot />
          </div>
          <!-- Footer -->
          <div v-if="$slots.footer"
               class="px-6 py-4 bg-gray-50 border-t border-gray-100 flex justify-end gap-3">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: Boolean,
  title:      { type: String, default: '' },
  size:       { type: String, default: 'md' }
})

defineEmits(['update:modelValue'])

const sizeClass = computed(() => ({
  sm: 'max-w-sm',
  md: 'max-w-lg',
  lg: 'max-w-2xl',
  xl: 'max-w-4xl'
}[props.size] || 'max-w-lg'))
</script>

<style scoped>
.modal-enter-active, .modal-leave-active { transition: opacity 0.2s ease; }
.modal-enter-from,  .modal-leave-to      { opacity: 0; }
</style>