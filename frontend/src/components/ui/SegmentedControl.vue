<!-- SegmentedControl — Tab-style selector for task type -->
<script setup>
const props = defineProps({
  modelValue: { type: String, required: true },
  options: {
    type: Array, // [{ value, label, icon? }]
    required: true,
  },
})
const emit = defineEmits(['update:modelValue'])
</script>

<template>
  <div
    role="tablist"
    :aria-label="$attrs['aria-label'] || 'Options'"
    class="inline-flex rounded-lg border border-[--border] bg-[--bg-subtle] p-0.5 gap-0.5"
  >
    <button
      v-for="opt in options"
      :key="opt.value"
      role="tab"
      :aria-selected="modelValue === opt.value"
      :tabindex="modelValue === opt.value ? 0 : -1"
      type="button"
      @click="emit('update:modelValue', opt.value)"
      :class="[
        'flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-all duration-150',
        modelValue === opt.value
          ? 'bg-[--surface] text-[--text-primary] shadow-[var(--shadow-card)]'
          : 'text-[--text-secondary] hover:text-[--text-primary]',
      ]"
    >
      <component v-if="opt.icon" :is="opt.icon" class="w-3.5 h-3.5 shrink-0" />
      {{ opt.label }}
    </button>
  </div>
</template>
