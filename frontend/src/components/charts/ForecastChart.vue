<!-- ForecastChart — Swiss Modern-Minimalist Style -->
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
  Filler,
} from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, PointElement, LineElement, CategoryScale, LinearScale, Filler)

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
  const labels = props.predictions.map((p, i) => p.timestamp || `+${i + 1}`)
  const values = props.predictions.map(p => Number(p.value).toFixed(2))

  return {
    labels,
    datasets: [
      {
        label: 'Forecast Trajectory',
        data: values,
        borderColor: '#10B981', // emerald
        backgroundColor: 'rgba(16, 185, 129, 0.08)',
        borderWidth: 2,
        pointBackgroundColor: '#10B981',
        pointBorderColor: '#FFFFFF',
        pointBorderWidth: 1.5,
        pointRadius: 4,
        pointHoverRadius: 6,
        fill: true,
        tension: 0.2,
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
        maxRotation: 45,
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
