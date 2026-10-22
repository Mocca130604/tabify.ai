<!-- StatusDot — small colored dot for engine status -->
<script setup>
defineProps({
  status: {
    type: String,
    default: 'loading', // ok | loading | error
    validator: (v) => ['ok', 'loading', 'error'].includes(v),
  },
  tooltip: { type: String, default: '' },
})
</script>

<template>
  <span
    :title="tooltip"
    :aria-label="tooltip"
    class="relative inline-flex h-2 w-2"
  >
    <!-- Pulse ring for loading -->
    <span
      v-if="status === 'loading'"
      class="animate-ping absolute inline-flex h-full w-full rounded-full bg-slate-400 opacity-60"
    />
    <span
      class="relative inline-flex rounded-full h-2 w-2"
      :class="
        status === 'ok'      ? 'bg-emerald-500' :
        status === 'error'   ? 'bg-red-500' :
                               'bg-slate-400'
      "
    />
  </span>
</template>
