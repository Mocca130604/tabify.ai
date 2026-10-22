<!-- StepIndicator — Modern Minimalist Swiss Stepper -->
<script setup>
import { usePredictionStore } from '../stores/predictionStore'
import { Check } from 'lucide-vue-next'

const store = usePredictionStore()

const steps = [
  { id: 1, title: 'Upload', desc: 'Dataset file' },
  { id: 2, title: 'Configure', desc: 'Task & target' },
  { id: 3, title: 'Run', desc: 'Inference' },
  { id: 4, title: 'Results', desc: 'Metrics & export' },
]

const canNavigateTo = (stepId) => {
  if (stepId === 1) return true
  if (stepId === 2 && store.inspectionData) return true
  if (stepId === 4 && store.predictionResult) return true
  return false
}
</script>

<template>
  <nav aria-label="Workflow progress" class="w-full">
    <div
      class="rounded-xl border border-[--border] bg-[--surface] px-4 sm:px-6 py-3.5 transition-colors"
      style="box-shadow: var(--shadow-card);"
    >
      <ol class="flex items-center justify-between">
        <li
          v-for="(step, idx) in steps"
          :key="step.id"
          class="flex-1 flex items-center"
        >
          <!-- Step button -->
          <button
            type="button"
            :disabled="!canNavigateTo(step.id) || store.isPredicting"
            @click="canNavigateTo(step.id) && store.goToStep(step.id)"
            :class="[
              'group inline-flex items-center gap-3 text-left transition-all select-none',
              canNavigateTo(step.id) && store.currentStep !== step.id ? 'cursor-pointer' : 'cursor-default',
              !canNavigateTo(step.id) && store.currentStep !== step.id ? 'opacity-40 cursor-not-allowed' : '',
            ]"
          >
            <!-- Number / Checkmark Badge -->
            <span
              :class="[
                'w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold shrink-0 transition-all duration-200',
                store.currentStep === step.id
                  ? 'bg-emerald-500 text-white ring-4 ring-emerald-500/20 shadow-md shadow-emerald-500/20'
                  : store.currentStep > step.id
                  ? 'bg-emerald-500/20 text-emerald-500'
                  : 'bg-[--bg-subtle] border border-[--border] text-[--text-muted]',
              ]"
            >
              <Check v-if="store.currentStep > step.id" class="w-3.5 h-3.5 stroke-[2.5]" />
              <span v-else>{{ step.id }}</span>
            </span>

            <!-- Step Titles -->
            <div class="hidden sm:block">
              <p
                :class="[
                  'text-xs font-semibold leading-tight tracking-tight',
                  store.currentStep === step.id
                    ? 'text-emerald-500 font-bold'
                    : store.currentStep > step.id
                    ? 'text-[--text-primary]'
                    : 'text-[--text-muted]',
                ]"
              >
                {{ step.title }}
              </p>
              <p class="text-[10px] text-[--text-muted] mt-0.5">
                {{ step.desc }}
              </p>
            </div>
          </button>

          <!-- Connecting Divider Line -->
          <div
            v-if="idx < steps.length - 1"
            class="flex-1 h-px mx-3 sm:mx-5 transition-colors"
            :class="store.currentStep > step.id ? 'bg-emerald-500' : 'bg-[--border]'"
          />
        </li>
      </ol>
    </div>
  </nav>
</template>
