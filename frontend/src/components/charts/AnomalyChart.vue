<!-- AnomalyChart — Swiss Modern-Minimalist Style -->
<script setup>
import { computed } from 'vue'
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
} from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

const props = defineProps({
  anomalyScores: {
    type: Array,
    required: true,
  },
  metrics: {
    type: Object,
    default: null,
  },
})

const threshold = computed(() => {
  return props.metrics?.anomaly_threshold_90p || 0.5
})

const chartData = computed(() => {
  const thresh = threshold.value
  const labels = props.anomalyScores.map((_, i) => `#${i + 1}`)
  const bgColors = props.anomalyScores.map(score =>
    score >= thresh ? '#DC2626' : '#CBD5E1'
  )

  return {
    labels,
    datasets: [
      {
        label: 'Anomaly Score',
        data: props.anomalyScores,
        backgroundColor: bgColors,
        borderRadius: 2,
        maxBarThickness: 16,
      },
    ],
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false,
    },
    tooltip: {
      backgroundColor: '#0F172A',
      titleColor: '#F8FAFC',
      bodyColor: '#E2E8F0',
      titleFont: { family: 'Inter', size: 12, weight: '600' },
      bodyFont: { family: 'Inter', size: 12 },
      padding: 10,
      cornerRadius: 6,
      displayColors: false,
      callbacks: {
        afterLabel: (context) => {
          const val = context.raw
          return val >= threshold.value ? 'Flagged Outlier (>= 90th percentile)' : 'In-distribution normal'
        },
      },
    },
  },
  scales: {
    x: {
      grid: { display: false },
      ticks: {
        color: '#94A3B8',
        font: { family: 'Inter', size: 11 },
        maxTicksLimit: 20,
      },
      border: { color: '#E2E8F0' },
    },
    y: {
      grid: {
        color: 'rgba(148, 163, 184, 0.15)',
      },
      ticks: {
        color: '#94A3B8',
        font: { family: 'Inter', size: 11 },
      },
      border: { dash: [4, 4], color: 'transparent' },
      min: 0,
      max: 1.0,
    },
  },
}
</script>

<template>
  <div class="space-y-3">
    <div class="h-64 sm:h-72 w-full">
      <Bar :data="chartData" :options="chartOptions" />
    </div>
    <div class="flex items-center justify-between text-xs text-[--text-muted] font-mono">
      <span class="inline-flex items-center gap-1.5">
        <span class="w-2 h-2 rounded-full bg-red-600 inline-block" />
        Outlier (score &ge; {{ Number(threshold).toFixed(3) }})
      </span>
      <span class="inline-flex items-center gap-1.5">
        <span class="w-2 h-2 rounded-full bg-slate-300 dark:bg-slate-600 inline-block" />
        Normal observations
      </span>
    </div>
  </div>
</template>
