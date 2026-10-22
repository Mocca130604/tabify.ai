<script setup>
import { onMounted, computed } from 'vue'
import { usePredictionStore } from './stores/predictionStore'
import { useTheme } from './composables/useTheme'
import Navbar from './components/Navbar.vue'
import StepIndicator from './components/StepIndicator.vue'
import DropZone from './components/DropZone.vue'
import ConfigureForm from './components/ConfigureForm.vue'
import RunPrediction from './components/RunPrediction.vue'
import ResultsView from './components/ResultsView.vue'
import { AlertCircle, Zap } from 'lucide-vue-next'

const store = usePredictionStore()
const { initTheme } = useTheme()

onMounted(() => {
  initTheme()
  store.fetchHealth()
})

const isOffline = computed(() => {
  return !store.isHealthLoading && store.systemHealth === null
})
</script>

<template>
  <div class="min-h-screen flex flex-col bg-[--bg] text-[--text-primary] transition-colors duration-200">
    <!-- 1. Minimal Header -->
    <Navbar />

    <!-- Backend offline notification banner -->
    <div
      v-if="isOffline"
      role="alert"
      class="border-b border-[--color-danger-border] bg-[--color-danger-subtle] dark:bg-red-950/40 text-[--color-danger] dark:text-red-300 text-xs py-2.5 px-4 text-center font-medium"
    >
      Inference backend is currently offline. Please ensure the local FastAPI server is running on port 8000.
    </div>

    <!-- 2. Main Content Container -->
    <main
      class="flex-1 w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-10 space-y-6 transition-all duration-200"
      :class="store.currentStep === 4 ? 'max-w-6xl' : 'max-w-5xl'"
    >
      <!-- Refined Header Section -->
      <div v-if="store.currentStep !== 4" class="text-center max-w-2xl mx-auto space-y-2.5">
        <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 dark:text-emerald-400 text-xs font-semibold">
          <Zap class="w-3.5 h-3.5 fill-current" />
          <span>Local TabPFN In-Context Foundation Engine</span>
        </div>
        <h1 class="text-2xl sm:text-3xl lg:text-4xl font-bold tracking-tight text-[--text-primary]">
          Instant Tabular Predictions
        </h1>
        <p class="text-xs sm:text-sm text-[--text-secondary] leading-relaxed max-w-xl mx-auto">
          Upload any CSV to get instantaneous in-context predictions from Prior Labs' foundation model running 100% locally on your hardware.
        </p>
      </div>

      <!-- Step Navigation Indicator -->
      <StepIndicator />

      <!-- Global Prediction Error Banner -->
      <div
        v-if="store.predictError"
        role="alert"
        class="rounded-xl border border-[--color-danger-border] bg-[--color-danger-subtle] dark:bg-red-950/30 p-4 text-xs text-[--color-danger] dark:text-red-300 flex items-start gap-3"
      >
        <AlertCircle class="w-4 h-4 shrink-0 mt-0.5" />
        <div class="space-y-0.5">
          <p class="font-semibold">
            {{ store.predictError.message }}
          </p>
          <p v-if="store.predictError.hint" class="opacity-90">
            Hint: {{ store.predictError.hint }}
          </p>
        </div>
      </div>

      <!-- 4-Step Dynamic Workflow -->
      <div>
        <!-- Step 1: Upload -->
        <DropZone v-if="store.currentStep === 1" />

        <!-- Step 2: Configure -->
        <ConfigureForm v-else-if="store.currentStep === 2" />

        <!-- Step 3: Run (Inference Progress) -->
        <RunPrediction v-else-if="store.currentStep === 3" />

        <!-- Step 4: Results (KPIs, Charts, Table) -->
        <ResultsView v-else-if="store.currentStep === 4" />
      </div>
    </main>

    <!-- 3. Minimal Footer -->
    <footer class="border-t border-[--border] py-6 mt-12 text-center text-xs text-[--text-muted]">
      <div class="max-w-6xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
        <p>Tabify.ai • Local TabPFN In-Context Foundation Engine</p>
        <div class="flex items-center gap-4">
          <a
            href="https://github.com/PriorLabs/TabPFN"
            target="_blank"
            rel="noopener noreferrer"
            class="hover:text-[--text-primary] transition-colors"
          >
            PriorLabs GitHub
          </a>
          <a
            href="https://huggingface.co/Prior-Labs"
            target="_blank"
            rel="noopener noreferrer"
            class="hover:text-[--text-primary] transition-colors"
          >
            Hugging Face Weights
          </a>
        </div>
      </div>
    </footer>
  </div>
</template>
