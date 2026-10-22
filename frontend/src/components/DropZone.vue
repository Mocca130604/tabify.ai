<!-- DropZone — Elegant Swiss File Ingestion -->
<script setup>
import { ref } from 'vue'
import { usePredictionStore } from '../stores/predictionStore'
import AppButton from './ui/AppButton.vue'
import {
  UploadCloud,
  FileSpreadsheet,
  AlertCircle,
  Tag,
  TrendingUp,
  Activity,
  ShieldAlert,
  ArrowRight,
  Sparkles,
} from 'lucide-vue-next'

const store = usePredictionStore()
const fileInput = ref(null)
const isDragging = ref(false)
const localError = ref(null)

const sampleDatasets = [
  {
    name: 'Iris Flower',
    filename: 'iris.csv',
    task: 'Classification',
    icon: Tag,
    badgeClass: 'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800',
    meta: '150 rows • 4 features',
    desc: 'Multi-class species categorization from flower measurements.',
  },
  {
    name: 'House Prices',
    filename: 'house_prices.csv',
    task: 'Regression',
    icon: TrendingUp,
    badgeClass: 'bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-950/40 dark:text-blue-300 dark:border-blue-800',
    meta: '50 rows • 3 features',
    desc: 'Continuous real-estate valuation estimation.',
  },
  {
    name: 'Daily Store Sales',
    filename: 'daily_sales.csv',
    task: 'Forecast',
    icon: Activity,
    badgeClass: 'bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-800',
    meta: '73 days • time-series',
    desc: 'Sequence extrapolation with calendar & foot-traffic factors.',
  },
  {
    name: 'Sensor Anomaly',
    filename: 'sensor_anomaly.csv',
    task: 'Anomaly',
    icon: ShieldAlert,
    badgeClass: 'bg-rose-50 text-rose-700 border-rose-200 dark:bg-rose-950/40 dark:text-rose-300 dark:border-rose-800',
    meta: '50 rows • unsupervised',
    desc: 'Density outlier detection with injected sensor spikes.',
  },
]

const validateAndUpload = (file) => {
  localError.value = null
  if (!file) return

  if (!file.name.toLowerCase().endsWith('.csv')) {
    localError.value = 'Only standard CSV (.csv) files are supported.'
    return
  }

  // Max 10MB
  const maxBytes = 10 * 1024 * 1024
  if (file.size > maxBytes) {
    localError.value = 'File size exceeds maximum 10 MB limit.'
    return
  }

  store.setFileAndInspect(file)
}

const handleFileSelect = (event) => {
  const file = event.target.files?.[0]
  if (file) {
    validateAndUpload(file)
  }
}

const handleDrop = (event) => {
  isDragging.value = false
  const file = event.dataTransfer?.files?.[0]
  if (file) {
    validateAndUpload(file)
  }
}

const openPicker = () => {
  if (fileInput.value && !store.isInspecting) {
    fileInput.value.click()
  }
}

const onKeyDown = (event) => {
  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault()
    openPicker()
  }
}

const loadSampleDataset = async (sample) => {
  localError.value = null
  try {
    const res = await fetch(`/sample_data/${sample.filename}`)
    if (!res.ok) throw new Error(`Could not load sample ${sample.filename}`)
    const text = await res.text()
    const blob = new Blob([text], { type: 'text/csv' })
    const file = new File([blob], sample.filename, { type: 'text/csv' })
    validateAndUpload(file)
  } catch (err) {
    localError.value = `Failed to load sample dataset: ${err.message}`
  }
}
</script>

<template>
  <div class="space-y-6">
    <!-- Main Dropzone Box -->
    <div
      role="button"
      tabindex="0"
      aria-label="Upload CSV dataset. Drag and drop file or press Enter to browse"
      @keydown="onKeyDown"
      @click="openPicker"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="handleDrop"
      :class="[
        'rounded-2xl border-2 border-dashed p-10 sm:p-14 text-center transition-all duration-200 cursor-pointer',
        'bg-[--surface] focus:outline-none focus-visible:ring-2 focus-visible:ring-[--color-accent-progress]',
        isDragging
          ? 'border-emerald-500 bg-emerald-50/20 dark:bg-emerald-950/20 shadow-md'
          : 'border-[--border] hover:border-[--text-secondary] hover:bg-[--surface-hover]',
        store.isInspecting ? 'pointer-events-none opacity-60' : '',
      ]"
      style="box-shadow: var(--shadow-card);"
    >
      <input
        ref="fileInput"
        type="file"
        accept=".csv"
        class="hidden"
        @change="handleFileSelect"
      />

      <div class="max-w-md mx-auto space-y-4">
        <!-- Modern Line Upload Icon -->
        <div class="w-14 h-14 mx-auto rounded-2xl bg-[--bg-subtle] border border-[--border] flex items-center justify-center text-[--text-primary] shadow-sm">
          <UploadCloud class="w-7 h-7 stroke-[1.5]" />
        </div>

        <div class="space-y-1">
          <h3 class="text-base sm:text-lg font-semibold tracking-tight text-[--text-primary]">
            Upload your Tabular Dataset
          </h3>
          <p class="text-xs sm:text-sm text-[--text-secondary]">
            Drag and drop your CSV file here, or <span class="font-medium underline underline-offset-4 decoration-[--border]">browse your computer</span>
          </p>
        </div>

        <div class="pt-1 flex flex-wrap items-center justify-center gap-3">
          <AppButton
            variant="outline"
            size="sm"
            :loading="store.isInspecting"
            @click.stop="openPicker"
          >
            <FileSpreadsheet class="w-3.5 h-3.5 stroke-[1.5]" />
            <span>Select CSV file</span>
          </AppButton>
          <span class="text-xs text-[--text-muted]">
            Max 10 MB • UTF-8 CSV
          </span>
        </div>
      </div>
    </div>

    <!-- Inline Validation or Inspection Error -->
    <div
      v-if="localError || store.inspectError"
      role="alert"
      class="rounded-xl border border-[--color-danger-border] bg-[--color-danger-subtle] dark:bg-red-950/30 p-4 flex items-start gap-3 text-xs text-[--color-danger] dark:text-red-300"
    >
      <AlertCircle class="w-4 h-4 shrink-0 mt-0.5" />
      <div class="space-y-0.5">
        <p class="font-semibold">
          {{ localError || store.inspectError?.message }}
        </p>
        <p v-if="store.inspectError?.hint" class="opacity-90">
          {{ store.inspectError.hint }}
        </p>
      </div>
    </div>

    <!-- Sample Datasets Grid -->
    <div class="space-y-3 pt-2">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <Sparkles class="w-4 h-4 text-emerald-500" />
          <h4 class="text-xs font-semibold uppercase tracking-wider text-[--text-primary]">
            Ready-to-use sample datasets
          </h4>
        </div>
        <span class="text-xs text-[--text-muted]">Click to load instantly</span>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        <button
          v-for="sample in sampleDatasets"
          :key="sample.filename"
          type="button"
          @click="loadSampleDataset(sample)"
          :disabled="store.isInspecting"
          class="group rounded-xl border border-[--border] bg-[--surface] p-4 text-left transition-all duration-200 hover:border-emerald-500/60 hover:shadow-[var(--shadow-card-hover)] flex flex-col justify-between disabled:opacity-50"
          style="box-shadow: var(--shadow-card);"
        >
          <div>
            <div class="flex items-center justify-between mb-2.5">
              <span :class="['text-[11px] font-medium px-2 py-0.5 rounded-full border', sample.badgeClass]">
                {{ sample.task }}
              </span>
              <component :is="sample.icon" class="w-4 h-4 text-[--text-muted] group-hover:text-emerald-500 transition-colors" />
            </div>

            <p class="text-sm font-semibold text-[--text-primary] group-hover:text-emerald-600 dark:group-hover:text-emerald-400 transition-colors">
              {{ sample.name }}
            </p>

            <p class="text-xs text-[--text-secondary] mt-1 line-clamp-2 leading-relaxed">
              {{ sample.desc }}
            </p>
          </div>

          <div class="mt-4 pt-3 border-t border-[--border-subtle] flex items-center justify-between text-[11px]">
            <span class="text-[--text-muted] font-mono">{{ sample.meta }}</span>
            <span class="font-medium text-emerald-600 dark:text-emerald-400 group-hover:translate-x-0.5 transition-transform flex items-center gap-0.5">
              Load <ArrowRight class="w-3 h-3" />
            </span>
          </div>
        </button>
      </div>
    </div>
  </div>
</template>
