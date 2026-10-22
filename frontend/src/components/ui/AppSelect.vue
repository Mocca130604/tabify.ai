<!-- AppSelect — Premium Swiss Floating Dropdown (Linear / Raycast Style) -->
<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ChevronDown, Check, Search, Hash, AlignLeft, Calendar } from 'lucide-vue-next'

const props = defineProps({
  modelValue: {
    type: [String, Number],
    default: '',
  },
  options: {
    type: Array, // Array of strings or { value/name, label, dtype/sub }
    required: true,
  },
  placeholder: {
    type: String,
    default: 'Select column…',
  },
  disabled: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:modelValue'])

const isOpen = ref(false)
const selectRef = ref(null)
const searchQuery = ref('')

// Normalize options to { value, label, badge, iconType }
const normalizedOptions = computed(() => {
  return props.options.map(opt => {
    if (typeof opt === 'string') {
      return { value: opt, label: opt, badge: null, iconType: 'text' }
    }
    const val = opt.value ?? opt.name
    const label = opt.label ?? opt.name
    const badge = opt.dtype ?? opt.sub ?? null
    const lowerBadge = String(badge || '').toLowerCase()
    let iconType = 'text'
    if (lowerBadge.includes('int') || lowerBadge.includes('float') || lowerBadge.includes('num')) {
      iconType = 'number'
    } else if (lowerBadge.includes('date') || lowerBadge.includes('time')) {
      iconType = 'date'
    }
    return { value: val, label, badge, iconType }
  })
})

const filteredOptions = computed(() => {
  if (!searchQuery.value) return normalizedOptions.value
  const q = searchQuery.value.toLowerCase().trim()
  return normalizedOptions.value.filter(o =>
    o.label.toLowerCase().includes(q) || (o.badge && o.badge.toLowerCase().includes(q))
  )
})

const selectedOption = computed(() => {
  return normalizedOptions.value.find(o => o.value === props.modelValue) || null
})

const toggleOpen = () => {
  if (props.disabled) return
  isOpen.value = !isOpen.value
  if (isOpen.value) {
    searchQuery.value = ''
  }
}

const selectItem = (val) => {
  emit('update:modelValue', val)
  isOpen.value = false
}

const handleClickOutside = (e) => {
  if (selectRef.value && !selectRef.value.contains(e.target)) {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<template>
  <div ref="selectRef" class="relative w-full">
    <!-- Trigger Button -->
    <button
      type="button"
      :disabled="disabled"
      @click="toggleOpen"
      :class="[
        'w-full flex items-center justify-between gap-3 px-3.5 py-2.5 text-xs rounded-xl border text-left transition-all duration-200',
        'bg-[--surface] text-[--text-primary]',
        isOpen
          ? 'border-emerald-500 ring-2 ring-emerald-500/20 shadow-md'
          : 'border-[--border] hover:border-[--text-secondary]',
        disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer',
      ]"
      style="box-shadow: var(--shadow-card);"
    >
      <div class="flex items-center gap-2.5 truncate">
        <!-- Icon based on type -->
        <component
          :is="selectedOption?.iconType === 'number' ? Hash : selectedOption?.iconType === 'date' ? Calendar : AlignLeft"
          class="w-3.5 h-3.5 text-emerald-500 shrink-0"
        />

        <span v-if="selectedOption" class="font-semibold text-sm truncate text-[--text-primary]">
          {{ selectedOption.label }}
        </span>
        <span v-else class="text-[--text-muted] text-sm">
          {{ placeholder }}
        </span>

        <span
          v-if="selectedOption?.badge"
          class="text-[10px] font-mono px-2 py-0.5 rounded-full bg-[--bg-subtle] text-[--text-secondary] border border-[--border]"
        >
          {{ selectedOption.badge }}
        </span>
      </div>

      <ChevronDown
        :class="[
          'w-4 h-4 text-[--text-muted] shrink-0 transition-transform duration-200',
          isOpen ? 'rotate-180 text-emerald-500' : ''
        ]"
      />
    </button>

    <!-- Floating Dropdown Menu (Solid, High-Contrast, No Blank White) -->
    <transition
      enter-active-class="transition duration-150 ease-out"
      enter-from-class="transform scale-98 opacity-0 -translate-y-1"
      enter-to-class="transform scale-100 opacity-100 translate-y-0"
      leave-active-class="transition duration-100 ease-in"
      leave-from-class="transform scale-100 opacity-100 translate-y-0"
      leave-to-class="transform scale-98 opacity-0 -translate-y-1"
    >
      <div
        v-if="isOpen"
        class="absolute z-50 mt-2 w-full rounded-xl border border-[--border] overflow-hidden"
        style="background-color: var(--surface); box-shadow: 0 14px 35px -4px rgba(0, 0, 0, 0.4), 0 8px 16px -6px rgba(0, 0, 0, 0.3);"
      >
        <!-- Search filter if more than 5 options -->
        <div v-if="normalizedOptions.length > 5" class="p-2.5 border-b border-[--border] bg-[--bg-subtle]">
          <div class="relative">
            <Search class="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-[--text-muted]" />
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search column name or type…"
              class="w-full bg-[--surface] border border-[--border] text-[--text-primary] placeholder-[--text-muted] rounded-lg pl-8 pr-3 py-1.5 text-xs focus:outline-none focus:ring-1 focus:ring-emerald-500"
              @click.stop
            />
          </div>
        </div>

        <!-- Options list -->
        <div class="max-h-60 overflow-y-auto py-1.5 divide-y divide-[--border-subtle]">
          <div
            v-if="filteredOptions.length === 0"
            class="px-4 py-3 text-xs text-[--text-muted] text-center"
          >
            No matching columns found
          </div>

          <button
            v-for="opt in filteredOptions"
            :key="opt.value"
            type="button"
            @click="selectItem(opt.value)"
            :class="[
              'w-full flex items-center justify-between gap-3 px-3.5 py-2.5 text-left transition-all duration-150 cursor-pointer',
              modelValue === opt.value
                ? 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 font-semibold'
                : 'text-[--text-primary] hover:bg-[--surface-hover]',
            ]"
          >
            <div class="flex items-center gap-2.5 min-w-0 truncate">
              <!-- Type icon -->
              <component
                :is="opt.iconType === 'number' ? Hash : opt.iconType === 'date' ? Calendar : AlignLeft"
                :class="[
                  'w-3.5 h-3.5 shrink-0',
                  modelValue === opt.value ? 'text-emerald-500' : 'text-[--text-muted]'
                ]"
              />

              <!-- Label -->
              <span class="text-xs font-medium truncate">
                {{ opt.label }}
              </span>

              <!-- Data type badge -->
              <span
                v-if="opt.badge"
                :class="[
                  'text-[10px] font-mono px-2 py-0.5 rounded-full border',
                  modelValue === opt.value
                    ? 'bg-emerald-500/20 text-emerald-600 dark:text-emerald-300 border-emerald-500/30'
                    : 'bg-[--bg-subtle] text-[--text-muted] border-[--border]'
                ]"
              >
                {{ opt.badge }}
              </span>
            </div>

            <!-- Checkmark -->
            <Check
              v-if="modelValue === opt.value"
              class="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0 stroke-[2.5]"
            />
          </button>
        </div>
      </div>
    </transition>
  </div>
</template>
