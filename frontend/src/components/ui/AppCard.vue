<!-- AppCard — clean minimalist container -->
<script setup>
defineProps({
  as: { type: String, default: 'div' },
  padding: {
    type: String,
    default: 'default', // none | sm | default | lg
    validator: (v) => ['none', 'sm', 'default', 'lg'].includes(v),
  },
})
</script>

<template>
  <component
    :is="as"
    :class="[
      'rounded-xl border border-[--border] bg-[--surface] transition-colors',
      padding === 'none' ? 'p-0' :
      padding === 'sm' ? 'p-4' :
      padding === 'lg' ? 'p-8' :
      'p-6'
    ]"
    style="box-shadow: var(--shadow-card);"
  >
    <slot />
  </component>
</template>
