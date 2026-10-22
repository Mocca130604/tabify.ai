<!-- RegressionChart — Swiss Modern-Minimalist Style -->
<script setup>
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  PointElement,
  LineElement,
  CategoryScale,
  LinearScale,
} from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, PointElement, LineElement, CategoryScale, LinearScale)

const props = defineProps({
  predictions: {
    type: Array,
    required: true,
  },
  metrics: {
    type: Object,
    default: null,
  },
})

const chartData = computed(() => {
  const displayItems = props.predictions.slice(0, 30)
  const labels = displayItems.map((_, i) => `#${i + 1}`)
  const predicted = displayItems.map(p => Number(p.value).toFixed(2))
  const actual = displayItems.map(p => p.actual !== null && p.actual !== undefined ? Number(p.actual).toFixed(2) : null)

  const datasets = [
    {
      label: 'TabPFN Predicted',
      data: predicted,
      borderColor: '#10B981', // emerald
      backgroundColor: '#10B981',
      borderWidth: 2,
      tension: 0.15,
      pointRadius: 3,
      pointHoverRadius: 5,
    },
  ]

  if (actual.some(v => v !== null)) {
    datasets.unshift({
      label: 'Actual Ground Truth',
      data: actual,
      borderColor: '#94A3B8', // slate-400
      backgroundColor: '#94A3B8',
      borderWidth: 1.5,
      borderDash: [4, 4],
      tension: 0.15,
      pointRadius: 2.5,
    })
  }

  return { labels, datasets }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top',
      align: 'end',
      labels: {
        color: '#64748B',
        font: { family: 'Inter', size: 11, weight: '500' },
        boxWidth: 12,
        boxHeight: 2,
        usePointStyle: false,
      },
    },
    tooltip: {
      backgroundColor: '#0F172A',
      titleColor: '#F8FAFC',
      bodyColor: '#E2E8F0',
      titleFont: { family: 'Inter', size: 12, weight: '600' },
      bodyFont: { family: 'Inter', size: 12 },
      padding: 10,
      cornerRadius: 6,
    },
  },
  scales: {
    x: {
      grid: { display: false },
      ticks: {
        color: '#94A3B8',
        font: { family: 'Inter', size: 11 },
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
    },
  },
}
</script>

<template>
  <div class="h-64 sm:h-72 w-full">
    <Line :data="chartData" :options="chartOptions" />
  </div>
</template>
