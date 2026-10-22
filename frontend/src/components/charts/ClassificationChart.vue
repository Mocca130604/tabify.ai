<!-- ClassificationChart — Swiss Modern-Minimalist Style -->
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
  const counts = {}
  props.predictions.forEach(p => {
    const val = String(p.value)
    counts[val] = (counts[val] || 0) + 1
  })

  const labels = Object.keys(counts)
  const data = Object.values(counts)

  return {
    labels,
    datasets: [
      {
        label: 'Predictions',
        data,
        backgroundColor: '#10B981', // emerald accent
        hoverBackgroundColor: '#059669',
        borderRadius: 4,
        maxBarThickness: 48,
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
        precision: 0,
      },
      border: { dash: [4, 4], color: 'transparent' },
    },
  },
}
</script>

<template>
  <div class="h-64 sm:h-72 w-full">
    <Bar :data="chartData" :options="chartOptions" />
  </div>
</template>
