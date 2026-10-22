<!-- ProgressBar — linear indeterminate or determinate -->
<script setup>
defineProps({
  indeterminate: { type: Boolean, default: false },
  value: { type: Number, default: 0 }, // 0-100
  color: { type: String, default: 'blue' }, // blue | emerald
})
</script>

<template>
  <div
    role="progressbar"
    :aria-valuenow="indeterminate ? undefined : value"
    :aria-valuemin="0"
    :aria-valuemax="100"
    aria-label="Progress"
    class="relative h-0.5 w-full overflow-hidden rounded-full bg-[--border]"
  >
    <!-- Indeterminate sliding bar -->
    <div
      v-if="indeterminate"
      class="absolute inset-y-0 left-0 w-1/2 rounded-full animate-indeterminate"
      :class="color === 'emerald' ? 'bg-emerald-500' : 'bg-[--color-accent-progress]'"
    />
    <!-- Determinate fill -->
    <div
      v-else
      class="h-full rounded-full transition-all duration-300 ease-out"
      :class="color === 'emerald' ? 'bg-emerald-500' : 'bg-[--color-accent-progress]'"
      :style="{ width: `${Math.min(100, Math.max(0, value))}%` }"
    />
  </div>
</template>
