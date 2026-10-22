<!-- AppHeader — Clean Minimalist Navbar with Backdrop Blur -->
<script setup>
import { computed } from 'vue'
import { usePredictionStore } from '../stores/predictionStore'
import { useTheme } from '../composables/useTheme'
import StatusDot from './ui/StatusDot.vue'
import { Sun, Moon, FileText, RefreshCw } from 'lucide-vue-next'

const store = usePredictionStore()
const { isDark, toggleTheme } = useTheme()

const healthStatus = computed(() => {
  if (store.isHealthLoading && !store.systemHealth) return 'loading'
  if (store.systemHealth?.status === 'ok') return 'ok'
  return 'error'
})

const healthTooltip = computed(() => {
  if (store.isHealthLoading) return 'Connecting to TabPFN engine...'
  if (store.systemHealth) {
    const dev = (store.systemHealth.device || 'cpu').toUpperCase()
    const ver = store.systemHealth.version ? `v${store.systemHealth.version}` : 'ready'
    return `Engine ready • TabPFN ${ver} (${dev})`
  }
  return 'Inference engine unreachable'
})
</script>

<template>
  <header class="h-16 border-b border-[--border] bg-[--surface-translucent] backdrop-blur-md sticky top-0 z-40 transition-colors">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 h-full flex items-center justify-between">
      <!-- Left: Generated Brand Logo & Wordmark + Status Dot -->
      <div class="flex items-center gap-3">
        <div class="relative w-9 h-9 rounded-xl overflow-hidden bg-white shadow-sm border border-[--border] flex items-center justify-center shrink-0">
          <img src="/tabify-logo.png" alt="Tabify.ai Logo" class="w-full h-full object-contain p-0.5" />
        </div>
        <div class="flex items-center gap-2">
          <span class="font-bold text-lg tracking-tight text-[--text-primary]">
            Tabify<span class="text-emerald-500 font-extrabold">.ai</span>
          </span>
          <span class="hidden sm:inline-block text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-full bg-[--bg-subtle] text-[--text-secondary] border border-[--border]">
            TabPFN v2
          </span>
        </div>
        <div class="flex items-center ml-1" :title="healthTooltip">
          <StatusDot :status="healthStatus" :tooltip="healthTooltip" />
        </div>
      </div>

      <!-- Right: Actions (Refresh, Docs, Theme toggle) -->
      <div class="flex items-center gap-2 sm:gap-3">
        <!-- Status refresh button -->
        <button
          type="button"
          @click="store.fetchHealth"
          :title="healthTooltip"
          class="p-2 rounded-lg text-[--text-secondary] hover:text-[--text-primary] hover:bg-[--bg-subtle] transition-colors"
          aria-label="Refresh engine status"
        >
          <RefreshCw :class="['w-4 h-4', store.isHealthLoading ? 'animate-spin text-emerald-500' : '']" />
        </button>

        <a
          href="https://github.com/PriorLabs/TabPFN"
          target="_blank"
          rel="noopener noreferrer"
          class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-[--text-secondary] hover:text-[--text-primary] hover:bg-[--bg-subtle] rounded-lg border border-[--border] transition-colors"
        >
          <FileText class="w-3.5 h-3.5" />
          <span>Docs</span>
        </a>

        <!-- Dark / Light toggle -->
        <button
          type="button"
          @click="toggleTheme"
          :aria-label="isDark ? 'Switch to light mode' : 'Switch to dark mode'"
          class="p-2 rounded-lg text-[--text-secondary] hover:text-[--text-primary] hover:bg-[--bg-subtle] border border-[--border] transition-colors"
        >
          <Sun v-if="isDark" class="w-4 h-4 text-amber-400" />
          <Moon v-else class="w-4 h-4" />
        </button>
      </div>
    </div>
  </header>
</template>
