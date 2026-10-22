<!-- ResultsView — Swiss AI Model Inference Dashboard -->
<script setup>
import { ref, computed } from 'vue'
import { usePredictionStore } from '../stores/predictionStore'
import AppButton from './ui/AppButton.vue'
import AppBadge from './ui/AppBadge.vue'
import ClassificationChart from './charts/ClassificationChart.vue'
import RegressionChart from './charts/RegressionChart.vue'
import ForecastChart from './charts/ForecastChart.vue'
import AnomalyChart from './charts/AnomalyChart.vue'
import {
  Download,
  RotateCcw,
  Sliders,
  ChevronLeft,
  ChevronRight,
  Search,
  CheckCircle2,
  Clock,
  Layers,
  BarChart2,
} from 'lucide-vue-next'

const store = usePredictionStore()

const currentPage = ref(1)
const pageSize = ref(10)
const searchQuery = ref('')

const result = computed(() => store.predictionResult)
const task = computed(() => result.value?.task || store.selectedTask)
const metrics = computed(() => result.value?.metrics || {})
const summary = computed(() => result.value?.summary || {})
const modelInfo = computed(() => result.value?.model_info || {})
const predictions = computed(() => result.value?.predictions || [])

// 3 KPI Cards
const kpiCards = computed(() => {
  const cards = []

  // Card 1: Primary Task Metric
  if (task.value === 'classification') {
    cards.push({
      label: 'Model Accuracy',
      value: metrics.value.accuracy !== undefined ? (metrics.value.accuracy * 100).toFixed(1) + '%' : 'N/A',
      sub: metrics.value.f1_macro !== undefined ? `Macro F1: ${metrics.value.f1_macro.toFixed(3)}` : 'In-context evaluation',
      icon: CheckCircle2,
      accent: 'text-emerald-600 dark:text-emerald-400',
    })
  } else if (task.value === 'regression') {
    cards.push({
      label: 'R² Score / MAE',
      value: metrics.value.r2_score !== undefined ? metrics.value.r2_score.toFixed(4) : (metrics.value.mae !== undefined ? metrics.value.mae.toFixed(2) : 'N/A'),
      sub: metrics.value.mae !== undefined ? `Mean Absolute Error: ${metrics.value.mae.toFixed(2)}` : 'Hold-out validation',
      icon: BarChart2,
      accent: 'text-blue-600 dark:text-blue-400',
    })
  } else if (task.value === 'forecast') {
    cards.push({
      label: 'Forecast Trajectory',
      value: metrics.value.validation_mae !== undefined ? `MAE ${metrics.value.validation_mae.toFixed(2)}` : `${metrics.value.forecast_horizon || 10} steps`,
      sub: `${metrics.value.forecast_horizon || 10} future horizon extrapolation`,
      icon: BarChart2,
      accent: 'text-amber-600 dark:text-amber-400',
    })
  } else if (task.value === 'anomaly') {
    cards.push({
      label: 'Anomalies Detected',
      value: metrics.value.detected_anomalies_count !== undefined ? String(metrics.value.detected_anomalies_count) : 'N/A',
      sub: metrics.value.anomaly_rate_percent !== undefined ? `${metrics.value.anomaly_rate_percent}% outlier frequency` : 'Unsupervised score',
      icon: CheckCircle2,
      accent: 'text-rose-600 dark:text-rose-400',
    })
  }

  // Card 2: Predictions completed
  const totalCount = predictions.value.length || summary.value.rows_predict || 0
  cards.push({
    label: 'Predictions Evaluated',
    value: String(totalCount),
    sub: summary.value.rows_train ? `Context: ${summary.value.rows_train} training rows` : 'Instant forward-pass evaluation',
    icon: Layers,
    accent: 'text-[--text-primary]',
  })

  // Card 3: Inference Duration
  const durationSec = summary.value.duration_ms ? (summary.value.duration_ms / 1000).toFixed(2) + 's' : '< 1s'
  const activeDevice = (modelInfo.value.device || store.selectedDevice || 'cpu').toUpperCase()
  cards.push({
    label: 'Inference Time',
    value: durationSec,
    sub: `Executed on local ${activeDevice} hardware`,
    icon: Clock,
    accent: 'text-emerald-600 dark:text-emerald-400',
  })

  return cards
})

// Filtered and paginated rows
const filteredRows = computed(() => {
  if (!searchQuery.value) return predictions.value
  const query = searchQuery.value.toLowerCase().trim()
  return predictions.value.filter(p => {
    return (
      String(p.row_index).includes(query) ||
      String(p.value).toLowerCase().includes(query) ||
      (p.actual !== null && String(p.actual).toLowerCase().includes(query)) ||
      (p.timestamp && String(p.timestamp).toLowerCase().includes(query))
    )
  })
})

const totalPages = computed(() => Math.ceil(filteredRows.value.length / pageSize.value) || 1)

const paginatedRows = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredRows.value.slice(start, start + pageSize.value)
})

const exportToCsv = () => {
  if (!predictions.value || predictions.value.length === 0) return

  let headers = ['row_index', 'prediction_value', 'actual_value']
  if (task.value === 'forecast') headers.push('forecast_timestamp')
  if (task.value === 'anomaly') headers.push('anomaly_score', 'is_outlier')
  if (task.value === 'classification') headers.push('confidence_probabilities')

  const rows = predictions.value.map(p => {
    const row = [p.row_index, p.value, p.actual ?? '']
    if (task.value === 'forecast') row.push(p.timestamp ?? '')
    if (task.value === 'anomaly') {
      row.push(p.probability?.anomaly_score ?? '', p.value)
    }
    if (task.value === 'classification') {
      row.push(p.probability ? JSON.stringify(p.probability).replace(/"/g, '""') : '')
    }
    return row.map(v => `"${v}"`).join(',')
  })

  const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows].join('\n')
  const encodedUri = encodeURI(csvContent)
  const link = document.createElement('a')
  link.setAttribute('href', encodedUri)
  link.setAttribute('download', `tabify_${task.value}_results.csv`)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}
</script>

<template>
  <div v-if="result" class="space-y-6 animate-fade-in">
    <!-- Top Action / Control Bar -->
    <div
      class="rounded-xl border border-[--border] bg-[--surface] p-4 sm:p-5 flex flex-wrap items-center justify-between gap-4"
      style="box-shadow: var(--shadow-card);"
    >
      <div class="space-y-1">
        <div class="flex items-center gap-2">
          <h3 class="text-base font-semibold text-[--text-primary]">
            Inference Completed
          </h3>
          <AppBadge variant="success">
            {{ task.toUpperCase() }}
          </AppBadge>
        </div>
        <p class="text-xs text-[--text-secondary] font-mono">
          Engine: {{ modelInfo.name }} • Device: {{ (modelInfo.device || store.selectedDevice || 'CPU').toUpperCase() }}
        </p>
      </div>

      <div class="flex items-center gap-2.5">
        <AppButton
          variant="outline"
          size="sm"
          @click="store.goToStep(2)"
        >
          <Sliders class="w-3.5 h-3.5 stroke-[1.5]" />
          <span>Adjust Config</span>
        </AppButton>

        <AppButton
          variant="outline"
          size="sm"
          @click="store.resetAll"
        >
          <RotateCcw class="w-3.5 h-3.5 stroke-[1.5]" />
          <span>Start Over</span>
        </AppButton>
      </div>
    </div>

    <!-- 3 KPI Cards Row -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <div
        v-for="(kpi, idx) in kpiCards"
        :key="idx"
        class="rounded-xl border border-[--border] bg-[--surface] p-5 flex flex-col justify-between"
        style="box-shadow: var(--shadow-card);"
      >
        <div class="flex items-center justify-between">
          <span class="text-xs font-semibold text-[--text-secondary] uppercase tracking-wider">
            {{ kpi.label }}
          </span>
          <component :is="kpi.icon" class="w-4 h-4 text-[--text-muted]" />
        </div>
        <div class="my-3">
          <div :class="['text-3xl font-bold tracking-tight tabular-nums', kpi.accent]">
            {{ kpi.value }}
          </div>
        </div>
        <div v-if="kpi.sub" class="text-xs text-[--text-muted] font-mono border-t border-[--border-subtle] pt-2">
          {{ kpi.sub }}
        </div>
      </div>
    </div>

    <!-- Interactive Task Visual Chart Card -->
    <div
      class="rounded-xl border border-[--border] bg-[--surface] p-5 sm:p-6 space-y-4"
      style="box-shadow: var(--shadow-card);"
    >
      <div class="flex items-center justify-between border-b border-[--border] pb-3">
        <div>
          <h4 class="text-xs font-semibold uppercase tracking-wider text-[--text-primary]">
            {{ task === 'classification' ? 'Class Distribution & Confidence' : task === 'regression' ? 'Predicted vs Actual Curve' : task === 'forecast' ? 'Forward Horizon Trajectory' : 'Anomaly Score Distribution' }}
          </h4>
          <p class="text-xs text-[--text-muted] mt-0.5">
            Interactive visualization of model outputs
          </p>
        </div>
        <AppBadge variant="default">
          Chart.js
        </AppBadge>
      </div>

      <div class="pt-2">
        <ClassificationChart
          v-if="task === 'classification'"
          :predictions="predictions"
          :metrics="metrics"
        />
        <RegressionChart
          v-else-if="task === 'regression'"
          :predictions="predictions"
          :metrics="metrics"
        />
        <ForecastChart
          v-else-if="task === 'forecast'"
          :predictions="predictions"
          :metrics="metrics"
        />
        <AnomalyChart
          v-else-if="task === 'anomaly'"
          :anomaly-scores="result.anomaly_scores || []"
          :metrics="metrics"
        />
      </div>
    </div>

    <!-- Results Table with Search & Pagination -->
    <div
      class="rounded-xl border border-[--border] bg-[--surface] overflow-hidden"
      style="box-shadow: var(--shadow-card);"
    >
      <!-- Table Top Toolbar -->
      <div class="px-5 py-4 border-b border-[--border] flex flex-wrap items-center justify-between gap-3 bg-[--bg-subtle]">
        <div>
          <h4 class="text-xs font-semibold uppercase tracking-wider text-[--text-primary]">
            Predictions Table
          </h4>
          <p class="text-xs text-[--text-muted] font-mono mt-0.5">
            Displaying {{ filteredRows.length }} total rows
          </p>
        </div>

        <div class="flex items-center gap-3">
          <!-- Search input -->
          <div class="relative">
            <Search class="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-[--text-muted]" />
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search table…"
              class="bg-[--surface] border border-[--border] text-[--text-primary] placeholder-[--text-muted] rounded-lg pl-8 pr-3 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-[--color-accent-progress] w-40 sm:w-56"
            />
          </div>

          <!-- Export CSV Button -->
          <AppButton
            variant="outline"
            size="sm"
            @click="exportToCsv"
          >
            <Download class="w-3.5 h-3.5 stroke-[1.5]" />
            <span>Export CSV</span>
          </AppButton>
        </div>
      </div>

      <!-- Clean Minimal Table -->
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse text-xs">
          <thead>
            <tr class="border-b border-[--border] bg-[--surface] text-[--text-secondary] uppercase text-[10px] tracking-wider font-semibold">
              <th class="px-4 py-3">Row</th>
              <th v-if="task === 'forecast'" class="px-4 py-3">Forecast Date</th>
              <th class="px-4 py-3">Predicted Output</th>
              <th v-if="task !== 'forecast' && task !== 'anomaly'" class="px-4 py-3">Actual Value</th>
              <th v-if="task === 'classification'" class="px-4 py-3">Top Confidence</th>
              <th v-if="task === 'anomaly'" class="px-4 py-3">Score</th>
              <th v-if="task === 'anomaly'" class="px-4 py-3">Status</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-[--border-subtle] font-mono">
            <tr
              v-for="p in paginatedRows"
              :key="p.row_index"
              :class="[
                'hover:bg-[--bg-subtle] transition-colors',
                task === 'anomaly' && p.value === true ? 'bg-red-50/50 dark:bg-red-950/20' : '',
              ]"
            >
              <td class="px-4 py-3 text-[--text-muted] tabular-nums">#{{ p.row_index }}</td>

              <td v-if="task === 'forecast'" class="px-4 py-3 text-[--text-primary]">
                {{ p.timestamp || '-' }}
              </td>

              <!-- Prediction Output column -->
              <td class="px-4 py-3 font-medium text-[--text-primary] tabular-nums">
                <span v-if="task === 'anomaly'">
                  <AppBadge :variant="p.value ? 'danger' : 'default'">
                    {{ p.value ? 'Outlier' : 'Normal' }}
                  </AppBadge>
                </span>
                <span v-else-if="task === 'classification'">
                  <AppBadge variant="default">
                    {{ p.value }}
                  </AppBadge>
                </span>
                <span v-else>
                  {{ typeof p.value === 'number' ? Number(p.value).toFixed(2) : p.value }}
                </span>
              </td>

              <!-- Actual Value -->
              <td v-if="task !== 'forecast' && task !== 'anomaly'" class="px-4 py-3 text-[--text-secondary] tabular-nums">
                {{ p.actual !== null && p.actual !== undefined ? p.actual : '-' }}
              </td>

              <!-- Confidence -->
              <td v-if="task === 'classification'" class="px-4 py-3 tabular-nums">
                <span v-if="p.probability" class="text-[--text-secondary]">
                  {{ (Math.max(...Object.values(p.probability)) * 100).toFixed(1) }}%
                </span>
                <span v-else class="text-[--text-muted]">-</span>
              </td>

              <!-- Anomaly Score -->
              <td
                v-if="task === 'anomaly'"
                class="px-4 py-3 tabular-nums font-semibold"
                :class="p.probability?.anomaly_score >= (metrics.anomaly_threshold_90p || 0.5) ? 'text-[--color-danger]' : 'text-[--text-secondary]'"
              >
                {{ p.probability?.anomaly_score !== undefined ? p.probability.anomaly_score.toFixed(4) : '-' }}
              </td>

              <!-- Anomaly status pill -->
              <td v-if="task === 'anomaly'" class="px-4 py-3">
                <AppBadge :variant="p.value ? 'danger' : 'default'">
                  {{ p.value ? 'Outlier' : 'Normal' }}
                </AppBadge>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination Footer -->
      <div class="px-5 py-3.5 border-t border-[--border] flex items-center justify-between text-xs text-[--text-secondary] bg-[--bg-subtle]">
        <div class="tabular-nums">
          Page {{ currentPage }} of {{ totalPages }}
        </div>
        <div class="flex items-center gap-2">
          <button
            type="button"
            :disabled="currentPage === 1"
            @click="currentPage--"
            class="p-1.5 rounded-lg border border-[--border] bg-[--surface] text-[--text-secondary] hover:text-[--text-primary] disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            aria-label="Previous page"
          >
            <ChevronLeft class="w-4 h-4 stroke-[1.5]" />
          </button>
          <button
            type="button"
            :disabled="currentPage >= totalPages"
            @click="currentPage++"
            class="p-1.5 rounded-lg border border-[--border] bg-[--surface] text-[--text-secondary] hover:text-[--text-primary] disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            aria-label="Next page"
          >
            <ChevronRight class="w-4 h-4 stroke-[1.5]" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
