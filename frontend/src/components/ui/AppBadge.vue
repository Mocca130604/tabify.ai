<!-- AppBadge — pill badge: default / success / danger / warning / info -->
<script setup>
defineProps({
  variant: {
    type: String,
    default: 'default',
    validator: (v) => ['default', 'success', 'danger', 'warning', 'info'].includes(v),
  },
})
</script>

<template>
  <span
    :class="[
      'inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-medium border',
      variant === 'success'
        ? 'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800'
        : variant === 'danger'
        ? 'bg-red-50 text-red-700 border-red-200 dark:bg-red-950/40 dark:text-red-300 dark:border-red-800'
        : variant === 'warning'
        ? 'bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-800'
        : variant === 'info'
        ? 'bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-950/40 dark:text-blue-300 dark:border-blue-800'
        : 'bg-[--bg-subtle] text-[--text-secondary] border-[--border]',
    ]"
  >
    <slot />
  </span>
</template>
