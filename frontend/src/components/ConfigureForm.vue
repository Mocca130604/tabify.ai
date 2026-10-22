<!-- ConfigureForm — Professional Swiss AI Configuration -->
<script setup>
import { computed } from 'vue'
import { usePredictionStore } from '../stores/predictionStore'
import AppButton from './ui/AppButton.vue'
import AppBadge from './ui/AppBadge.vue'
import AppSelect from './ui/AppSelect.vue'
import {
  FileText,
  RotateCcw,
  Table,
  Check,
  Lock,
  Loader2,
  Cpu,
  AlertTriangle,
  ArrowRight,
  Tag,
  TrendingUp,
  Activity,
  ShieldAlert,
  Sparkles,
} from 'lucide-vue-next'

const store = usePredictionStore()

const taskDefinitions = [
  {
    id: 'classification',
    title: 'Classification',
    subtitle: 'Categorical targets',
    icon: Tag,
    desc: 'TabPFNClassifier predicts categorical classes in-context.',
  },
  {
    id: 'regression',
    title: 'Regression',
    subtitle: 'Continuous values',
    icon: TrendingUp,
    desc: 'TabPFNRegressor predicts real numerical targets.',
  },
  {
    id: 'forecast',
    title: 'Forecast',
    subtitle: 'Time-series sequence',
    icon: Activity,
    desc: 'Extrapolates future chronological horizon values.',
  },
  {
    id: 'anomaly',
    title: 'Anomaly',
    subtitle: 'Outlier detection',
    icon: ShieldAlert,
    desc: 'Unsupervised multivariate outlier deviation density.',
  },
]

const formatFileSize = (bytes) => {
  if (!bytes) return ''
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

const onTaskChange = (taskId) => {
  store.selectedTask = taskId
  if (taskId !== 'anomaly' && !store.selectedTarget && store.columns.length > 0) {
    if (store.inspectionData?.suggestions?.recommended_target) {
      store.selectedTarget = store.inspectionData.suggestions.recommended_target
    } else {
      store.selectedTarget = store.columns[store.columns.length - 1].name
    }
  }
}

// Device catalog
const deviceCatalog = computed(() => store.systemHealth?.device_catalog ?? [])

const isDeviceActive = (d) => {
  return store.selectedDevice === d.id && d.available
}

const removeFile = () => {
  store.resetAll()
}
</script>

<template>
  <div class="space-y-6 animate-fade-in">
    <!-- 1. File Info Header Bar -->
    <div
      class="rounded-xl border border-[--border] bg-[--surface] p-4 flex flex-wrap items-center justify-between gap-3"
      style="box-shadow: var(--shadow-card);"
    >
      <div class="flex items-center gap-3 min-w-0">
        <div class="w-9 h-9 rounded-lg bg-[--bg-subtle] border border-[--border] flex items-center justify-center text-[--text-primary] shrink-0">
          <FileText class="w-4 h-4 stroke-[1.5]" />
        </div>
        <div class="min-w-0">
          <div class="flex items-center gap-2 flex-wrap">
            <span class="font-semibold text-sm text-[--text-primary] truncate font-mono">
              {{ store.inspectionData?.filename || store.selectedFile?.name || 'dataset.csv' }}
            </span>
            <AppBadge variant="default">
              {{ store.inspectionData?.row_count }} rows
            </AppBadge>
            <AppBadge variant="default">
              {{ store.inspectionData?.column_count }} columns
            </AppBadge>
            <span v-if="store.selectedFile?.size" class="text-xs text-[--text-muted]">
              {{ formatFileSize(store.selectedFile.size) }}
            </span>
          </div>
        </div>
      </div>

      <AppButton
        variant="ghost"
        size="sm"
        @click="removeFile"
        class="text-[--text-secondary] hover:text-[--color-danger]"
      >
        <RotateCcw class="w-3.5 h-3.5 stroke-[1.5]" />
        <span>Change dataset</span>
      </AppButton>
    </div>

    <!-- Sanitized Columns Alert (if any) -->
    <div
      v-if="store.inspectionData?.dropped_columns && store.inspectionData.dropped_columns.length > 0"
      class="rounded-xl border border-amber-200 bg-amber-50 dark:bg-amber-950/30 dark:border-amber-900/60 p-4 flex items-start gap-3 text-xs text-amber-800 dark:text-amber-200"
    >
      <AlertTriangle class="w-4 h-4 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
      <div class="space-y-1">
        <p class="font-semibold">Notice on Sanitized Columns</p>
        <p class="opacity-90">
          The following constant or ID column(s) were excluded from training features:
        </p>
        <ul class="list-disc list-inside space-y-0.5 font-mono text-[11px]">
          <li v-for="d in store.inspectionData.dropped_columns" :key="d.column">
            <span class="font-semibold">{{ d.column }}</span>: {{ d.reason }}
          </li>
        </ul>
      </div>
    </div>

    <!-- 2. Data Preview Table Card -->
    <div
      class="rounded-xl border border-[--border] bg-[--surface] overflow-hidden"
      style="box-shadow: var(--shadow-card);"
    >
      <div class="px-4 py-3 border-b border-[--border] flex items-center justify-between bg-[--bg-subtle]">
        <div class="flex items-center gap-2">
          <Table class="w-4 h-4 text-[--text-secondary]" />
          <h4 class="font-semibold text-xs text-[--text-primary] uppercase tracking-wider">
            Dataset Inspection Preview
          </h4>
        </div>
        <span class="text-xs text-[--text-muted] font-mono">
          Showing 5 preview rows
        </span>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse text-xs">
          <thead>
            <tr class="border-b border-[--border] bg-[--surface]">
              <th
                v-for="col in store.inspectionData?.columns"
                :key="col.name"
                class="px-4 py-2.5 font-medium text-[--text-secondary] text-[11px] whitespace-nowrap uppercase tracking-wider"
              >
                <div class="flex items-center gap-1.5">
                  <span class="font-semibold text-[--text-primary]">{{ col.name }}</span>
                  <span class="text-[10px] font-mono text-[--text-muted]">
                    {{ col.dtype }}
                  </span>
                </div>
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-[--border-subtle] font-mono">
            <tr
              v-for="(row, idx) in store.inspectionData?.preview_rows"
              :key="idx"
              class="hover:bg-[--bg-subtle] transition-colors"
            >
              <td
                v-for="col in store.inspectionData?.columns"
                :key="col.name"
                class="px-4 py-2.5 text-[--text-primary] whitespace-nowrap tabular-nums"
              >
                {{ row[col.name] !== null && row[col.name] !== undefined ? row[col.name] : '-' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 3. Machine Learning Task Selection (4 Interactive Cards) -->
    <div class="space-y-3">
      <div class="flex items-center justify-between">
        <label class="text-xs font-semibold uppercase tracking-wider text-[--text-secondary]">
          1. Select Machine Learning Task
        </label>
        <span v-if="store.inspectionData?.suggestions?.recommended_task" class="text-xs text-emerald-600 dark:text-emerald-400 font-medium flex items-center gap-1">
          <Sparkles class="w-3.5 h-3.5" />
          Recommended: {{ store.inspectionData.suggestions.recommended_task }}
        </span>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        <button
          v-for="t in taskDefinitions"
          :key="t.id"
          type="button"
          @click="onTaskChange(t.id)"
          :class="[
            'relative rounded-xl p-4 text-left transition-all duration-200 flex flex-col justify-between',
            store.selectedTask === t.id
              ? 'border-2 border-emerald-500 bg-[--surface] ring-2 ring-emerald-500/20 shadow-md shadow-emerald-500/10'
              : 'border border-[--border] bg-[--surface] hover:border-[--text-secondary] hover:bg-[--surface-hover]',
          ]"
          style="box-shadow: var(--shadow-card);"
        >
          <div>
            <div class="flex items-center justify-between mb-3">
              <div
                :class="[
                  'w-8 h-8 rounded-lg flex items-center justify-center transition-colors',
                  store.selectedTask === t.id ? 'bg-emerald-500/15 text-emerald-500' : 'bg-[--bg-subtle] text-[--text-muted]'
                ]"
              >
                <component :is="t.icon" class="w-4 h-4 stroke-[2]" />
              </div>

              <span
                v-if="store.selectedTask === t.id"
                class="w-5 h-5 rounded-full bg-emerald-500 text-white flex items-center justify-center shadow-sm"
              >
                <Check class="w-3 h-3 stroke-[3]" />
              </span>
            </div>

            <p :class="['text-sm font-semibold transition-colors', store.selectedTask === t.id ? 'text-emerald-500' : 'text-[--text-primary]']">
              {{ t.title }}
            </p>
            <p class="text-[11px] text-[--text-muted] font-medium mt-0.5">
              {{ t.subtitle }}
            </p>
          </div>

          <p class="text-xs text-[--text-secondary] mt-3 leading-relaxed">
            {{ t.desc }}
          </p>
        </button>
      </div>
    </div>

    <!-- 4. Parameters & Subsampling Card -->
    <div
      class="rounded-xl border border-[--border] bg-[--surface] p-5 space-y-4"
      style="box-shadow: var(--shadow-card);"
    >
      <label class="block text-xs font-semibold uppercase tracking-wider text-[--text-secondary]">
        2. Task Parameters & Inference Scope
      </label>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <!-- Target Column (Required for Classification, Regression, Forecast) -->
        <div v-if="store.selectedTask !== 'anomaly'" class="space-y-1.5">
          <label class="block text-xs font-medium text-[--text-primary]">
            Target column <span class="text-[--color-danger]">*</span>
          </label>
          <AppSelect
            v-model="store.selectedTarget"
            :options="store.columns"
            placeholder="Select target column…"
          />
          <p class="text-[11px] text-[--text-muted]">
            Column that the TabPFN foundation model will predict.
          </p>
        </div>

        <div v-else class="rounded-lg border border-[--border] bg-[--bg-subtle] p-3 text-xs text-[--text-secondary]">
          <p class="font-medium text-[--text-primary]">Unsupervised Task</p>
          <p class="text-[11px] text-[--text-muted] mt-1">
            No target column needed. TabPFN computes multivariate outlier deviation scores across all features.
          </p>
        </div>

        <!-- Time Column (Only for Forecast) -->
        <div v-if="store.selectedTask === 'forecast'" class="space-y-1.5">
          <label class="block text-xs font-medium text-[--text-primary]">
            Time / Date column <span class="text-[--color-danger]">*</span>
          </label>
          <AppSelect
            v-model="store.selectedTimeColumn"
            :options="store.columns"
            placeholder="Select time column…"
          />
        </div>

        <!-- Horizon (Only for Forecast) -->
        <div v-if="store.selectedTask === 'forecast'" class="space-y-1.5">
          <label class="block text-xs font-medium text-[--text-primary]">
            Forecast horizon (steps)
          </label>
          <input
            type="number"
            v-model.number="store.forecastHorizon"
            min="1"
            max="100"
            class="w-full bg-[--surface] border border-[--border] text-[--text-primary] rounded-lg px-3 py-2 text-xs focus:outline-none focus:ring-2 focus:ring-[--color-accent-progress] tabular-nums"
          />
        </div>
      </div>

      <!-- Subsample Checkbox -->
      <div class="pt-2 border-t border-[--border]">
        <label class="inline-flex items-center gap-2 cursor-pointer text-xs text-[--text-secondary]">
          <input
            type="checkbox"
            v-model="store.autoSubsample"
            class="rounded border-[--border] text-emerald-600 focus:ring-[--color-accent-progress]"
          />
          <span>Auto-subsample large tables (> 5,000 rows) for instantaneous evaluation</span>
        </label>
      </div>
    </div>

    <!-- 5. Compute Device Selection Card -->
    <div
      class="rounded-xl border border-[--border] bg-[--surface] p-5 space-y-3"
      style="box-shadow: var(--shadow-card);"
    >
      <div class="flex items-center justify-between">
        <label class="text-xs font-semibold uppercase tracking-wider text-[--text-secondary] flex items-center gap-1.5">
          <Cpu class="w-3.5 h-3.5 stroke-[1.5]" />
          3. Hardware Compute Device
        </label>
        <span v-if="store.isSwitchingDevice" class="flex items-center gap-1 text-xs text-[--color-accent-progress]">
          <Loader2 class="w-3 h-3 animate-spin" />
          Switching…
        </span>
        <span v-else class="text-xs text-[--text-muted] font-mono">
          Active: <strong class="text-emerald-600 dark:text-emerald-400">{{ store.selectedDevice?.toUpperCase() || 'CPU' }}</strong>
        </span>
      </div>

      <!-- Device Switch Error -->
      <div
        v-if="store.deviceSwitchError"
        class="rounded-lg border border-[--color-danger-border] bg-[--color-danger-subtle] dark:bg-red-950/30 p-2.5 text-xs text-[--color-danger]"
      >
        {{ store.deviceSwitchError }}
      </div>

      <!-- Minimalist Device Grid -->
      <div
        v-if="deviceCatalog.length > 0"
        class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5"
      >
        <button
          v-for="d in deviceCatalog"
          :key="d.vendor + d.id"
          type="button"
          :disabled="!d.available || store.isSwitchingDevice"
          @click="d.available && store.switchDeviceTo(d.id)"
          :class="[
            'relative rounded-xl p-3.5 text-left transition-all duration-200',
            isDeviceActive(d)
              ? 'border-2 border-emerald-500 bg-[--surface] ring-2 ring-emerald-500/20 shadow-md shadow-emerald-500/10'
              : d.available
              ? 'border border-[--border] bg-[--surface] hover:border-[--text-secondary] hover:bg-[--surface-hover] cursor-pointer'
              : 'border border-[--border] bg-[--bg-subtle] opacity-40 cursor-not-allowed',
          ]"
        >
          <div class="flex items-center justify-between mb-2">
            <span
              :class="[
                'text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full border transition-colors',
                isDeviceActive(d)
                  ? 'bg-emerald-500/15 text-emerald-500 border-emerald-500/30 font-extrabold'
                  : 'bg-[--bg-subtle] text-[--text-secondary] border-[--border]'
              ]"
            >
              {{ d.vendor }}
            </span>
            <span
              v-if="isDeviceActive(d)"
              class="w-5 h-5 rounded-full bg-emerald-500 text-white flex items-center justify-center shadow-sm"
            >
              <Check class="w-3 h-3 stroke-[3]" />
            </span>
            <Lock v-else-if="!d.available" class="w-3.5 h-3.5 text-[--text-muted]" />
          </div>

          <p :class="['text-xs font-semibold truncate transition-colors', isDeviceActive(d) ? 'text-emerald-500 font-bold' : 'text-[--text-primary]']">
            {{ d.label }}
          </p>

          <p class="text-[10px] text-[--text-muted] mt-1 font-mono">
            <span v-if="d.vram_gb">{{ d.vram_gb }} GB VRAM</span>
            <span v-else-if="d.id === 'cpu'">Always available</span>
            <span v-else-if="!d.available">Not detected</span>
          </p>
        </button>
      </div>
    </div>

    <!-- 6. Action Button Bar -->
    <div class="flex items-center justify-end pt-2">
      <AppButton
        variant="primary"
        size="lg"
        :disabled="!store.isConfigValid || store.isPredicting"
        @click="store.executePrediction"
      >
        <span>Run In-Context Inference</span>
        <ArrowRight class="w-4 h-4 stroke-[2]" />
      </AppButton>
    </div>
  </div>
</template>
