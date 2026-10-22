<!-- AppButton — primary / outline / ghost / danger variants -->
<script setup>
defineProps({
  variant: {
    type: String,
    default: 'primary', // primary | outline | ghost | danger
    validator: (v) => ['primary', 'outline', 'ghost', 'danger'].includes(v),
  },
  size: {
    type: String,
    default: 'md', // sm | md | lg
    validator: (v) => ['sm', 'md', 'lg'].includes(v),
  },
  disabled: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
  type: { type: String, default: 'button' },
})
</script>

<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    :class="[
      // base
      'inline-flex items-center justify-center gap-2 font-medium rounded-lg',
      'transition-all duration-200 ease-out select-none',
      'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[--color-accent-progress] focus-visible:ring-offset-2',
      'disabled:opacity-50 disabled:cursor-not-allowed',
      // size
      size === 'sm' ? 'px-3 py-1.5 text-xs' : size === 'lg' ? 'px-6 py-3 text-sm' : 'px-4 py-2 text-sm',
      // variant
      variant === 'primary'
        ? 'bg-[--text-primary] text-[--bg] hover:opacity-80 dark:bg-[--text-primary] dark:text-[--bg]'
        : variant === 'outline'
        ? 'border border-[--border] text-[--text-primary] hover:bg-[--bg-subtle] bg-transparent'
        : variant === 'danger'
        ? 'bg-[--color-danger] text-white hover:opacity-85'
        : /* ghost */ 'text-[--text-secondary] hover:text-[--text-primary] hover:bg-[--bg-subtle]',
    ]"
  >
    <!-- Loading spinner (minimal, line-based) -->
    <svg v-if="loading" class="animate-spin w-3.5 h-3.5 shrink-0" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3"/>
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
    </svg>
    <slot />
  </button>
</template>
