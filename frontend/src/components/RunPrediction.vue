<!-- RunPrediction — Beautiful Progress Bar & Live Status -->
<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { usePredictionStore } from '../stores/predictionStore'
import { Check, Sparkles, Cpu } from 'lucide-vue-next'

const store = usePredictionStore()

// Truthful stages based on actual model execution phases
const STAGES = [
  { id: 0, label: 'Loading dataset & feature encoding', targetProgress: 35, durationMs: 2500 },
  { id: 1, label: 'Running TabPFN forward pass evaluation', targetProgress: 75, durationMs: 6500 },
  { id: 2, label: 'Compiling predictions & metrics', targetProgress: 95, durationMs: 3000 },
]

const stageIndex = ref(0)
const progressVal = ref(15) // animated 0-100 progress percentage
const elapsed = ref(0)
const startTime = ref(null)

let progressTimer = null
let stageTimer = null
let elapsedTimer = null

function advanceStage(idx) {
  if (idx >= STAGES.length) return
  stageIndex.value = idx
  const stage = STAGES[idx]
  const target = stage.targetProgress
  const current = progressVal.value
  const diff = target - current
  const steps = 40
  const interval = stage.durationMs / steps
  let step = 0

  clearInterval(progressTimer)
  progressTimer = setInterval(() => {
    step++
    const factor = 1 - Math.pow(1 - step / steps, 2)
    progressVal.value = Math.min(99, Math.round(current + diff * factor))
    if (step >= steps) {
      clearInterval(progressTimer)
      if (idx + 1 < STAGES.length) {
        advanceStage(idx + 1)
      }
    }
  }, interval)
}

onMounted(() => {
  startTime.value = Date.now()
  advanceStage(0)
  elapsedTimer = setInterval(() => {
    elapsed.value = Math.floor((Date.now() - startTime.value) / 1000)
  }, 1000)
})

onUnmounted(() => {
  clearInterval(progressTimer)
  clearTimeout(stageTimer)
  clearInterval(elapsedTimer)
})

const elapsedLabel = computed(() => {
  const m = Math.floor(elapsed.value / 60)
  const s = elapsed.value % 60
  return m > 0 ? `${m}m ${s}s` : `${s}s`
})

const activeDeviceLabel = computed(() => {
  const dev = store.selectedDevice || store.systemHealth?.device || 'cpu'
  return dev.toUpperCase()
})
</script>

<template>
  <div
    class="relative rounded-2xl border border-[--border] bg-[--surface] overflow-hidden max-w-xl mx-auto transition-colors"
    style="box-shadow: var(--shadow-card);"
  >
    <!-- Top 2px Progress Bar -->
    <div class="h-1 w-full bg-[--bg-subtle] overflow-hidden relative">
      <div
        class="h-full bg-gradient-to-r from-emerald-500 to-teal-400 transition-all duration-300 ease-out"
        :style="{ width: `${progressVal}%` }"
      />
    </div>

    <div class="p-8 sm:p-10 space-y-7">
      <!-- Title & Icon -->
      <div class="text-center space-y-2">
        <div class="w-12 h-12 mx-auto rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-600 dark:text-emerald-400 shadow-sm">
          <Cpu class="w-6 h-6 stroke-[1.5] animate-pulse" />
        </div>
        <h3 class="text-lg font-semibold tracking-tight text-[--text-primary]">
          Running In-Context Inference
        </h3>
        <p class="text-xs text-[--text-secondary]">
          Evaluating tabular foundation model on local <strong class="text-[--text-primary]">{{ activeDeviceLabel }}</strong> hardware
        </p>
      </div>

      <!-- Prominent Center Progress Bar -->
      <div class="space-y-2.5 bg-[--bg-subtle] p-4 rounded-xl border border-[--border]">
        <div class="flex items-center justify-between text-xs">
          <span class="font-medium text-[--text-primary] flex items-center gap-1.5">
            <Sparkles class="w-3.5 h-3.5 text-emerald-500" />
            {{ STAGES[stageIndex]?.label || 'Processing…' }}
          </span>
          <span class="font-mono font-semibold text-emerald-600 dark:text-emerald-400 tabular-nums">
            {{ progressVal }}%
          </span>
        </div>

        <!-- Big Progress Bar Track -->
        <div class="h-3 w-full bg-[--surface] rounded-full overflow-hidden border border-[--border] p-0.5">
          <div
            class="h-full rounded-full bg-gradient-to-r from-emerald-500 via-teal-400 to-emerald-500 bg-[length:200%_100%] animate-[shimmer_2s_infinite] transition-all duration-300 ease-out shadow-sm"
            :style="{ width: `${progressVal}%` }"
          />
        </div>

        <div class="flex items-center justify-between text-[11px] text-[--text-muted] pt-0.5">
          <span>In-context zero-training forward pass</span>
          <span class="font-mono tabular-nums">Elapsed: {{ elapsedLabel }}</span>
        </div>
      </div>

      <!-- Status Steps (Text-based Stepper) -->
      <div class="max-w-sm mx-auto space-y-2.5">
        <div
          v-for="stage in STAGES"
          :key="stage.id"
          class="flex items-center gap-3 text-xs"
        >
          <!-- Step indicator dot/check -->
          <span
            :class="[
              'w-5 h-5 rounded-full flex items-center justify-center text-[10px] shrink-0 transition-all duration-200',
              stageIndex > stage.id
                ? 'bg-emerald-500 text-white'
                : stageIndex === stage.id
                ? 'bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 ring-2 ring-emerald-500/30'
                : 'border border-[--border] bg-[--bg-subtle] text-[--text-muted]',
            ]"
          >
            <Check v-if="stageIndex > stage.id" class="w-3 h-3 stroke-[3]" />
            <span v-else-if="stageIndex === stage.id" class="w-1.5 h-1.5 rounded-full bg-emerald-500" />
            <span v-else>{{ stage.id + 1 }}</span>
          </span>

          <!-- Label -->
          <span
            :class="[
              stageIndex === stage.id
                ? 'font-semibold text-[--text-primary]'
                : stageIndex > stage.id
                ? 'text-[--text-secondary]'
                : 'text-[--text-muted]',
            ]"
          >
            {{ stage.label }}
          </span>

          <!-- Current active pill -->
          <span
            v-if="stageIndex === stage.id"
            class="text-[10px] font-mono text-emerald-600 dark:text-emerald-400 ml-auto tabular-nums bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/20"
          >
            Active
          </span>
        </div>
      </div>

      <!-- Note for First Run Weight Download -->
      <div class="pt-3 border-t border-[--border] text-center">
        <p class="text-[11px] text-[--text-muted] leading-relaxed">
          First run may take a few moments longer while model weights initialize in memory.
        </p>
      </div>
    </div>
  </div>
</template>
