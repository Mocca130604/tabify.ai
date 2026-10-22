import { defineStore } from 'pinia'
import { getHealth, inspectCsv, runPrediction, switchDevice } from '../api/client'

export const usePredictionStore = defineStore('prediction', {
  state: () => ({
    // Navigation & steps (1: Upload, 2: Configure, 3: Run, 4: Results)
    currentStep: 1,

    // System Health
    systemHealth: null,
    isHealthLoading: false,

    // Compute Device
    selectedDevice: 'auto',    // 'auto' | 'cpu' | 'cuda' | 'mps'
    isSwitchingDevice: false,
    deviceSwitchError: null,

    // Step 1: File
    selectedFile: null,
    isInspecting: false,
    inspectError: null,

    // Step 2: Configuration & Inspection details
    inspectionData: null,
    selectedTask: 'classification',
    selectedTarget: '',
    selectedTimeColumn: '',
    forecastHorizon: 10,
    autoSubsample: true,

    // Step 3: Run / Inference
    isPredicting: false,
    predictError: null,

    // Step 4: Results
    predictionResult: null,
  }),

  getters: {
    isConfigValid(state) {
      if (!state.selectedFile || !state.inspectionData) return false
      if (state.selectedTask === 'anomaly') return true
      if (!state.selectedTarget) return false
      if (state.selectedTask === 'forecast' && !state.selectedTimeColumn) return false
      return true
    },
    columns(state) {
      return state.inspectionData?.columns || []
    },
    numericColumns(state) {
      if (!state.inspectionData) return []
      return state.inspectionData.columns
        .filter(c => ['int64', 'float64', 'number'].some(t => c.dtype.toLowerCase().includes(t)))
        .map(c => c.name)
    },
    categoricalColumns(state) {
      if (!state.inspectionData) return []
      return state.inspectionData.columns
        .filter(c => !['int64', 'float64', 'number'].some(t => c.dtype.toLowerCase().includes(t)))
        .map(c => c.name)
    },
    dateColumns(state) {
      if (!state.inspectionData) return []
      return state.inspectionData.columns
        .filter(c => c.dtype.toLowerCase().includes('datetime') || c.name.toLowerCase().includes('date') || c.name.toLowerCase().includes('time'))
        .map(c => c.name)
    },
  },

  actions: {
    async fetchHealth() {
      this.isHealthLoading = true
      try {
        this.systemHealth = await getHealth()
        // Sync selectedDevice with whatever the backend is currently using
        if (this.selectedDevice === 'auto' && this.systemHealth?.device) {
          this.selectedDevice = this.systemHealth.device
        }
      } catch (err) {
        console.warn('Backend not yet reachable on /api/health:', err)
      } finally {
        this.isHealthLoading = false
      }
    },

    async switchDeviceTo(deviceId) {
      if (this.isSwitchingDevice) return
      this.isSwitchingDevice = true
      this.deviceSwitchError = null
      try {
        const result = await switchDevice(deviceId)
        this.selectedDevice = result.active_device
        // Refresh health so device_catalog badges update
        await this.fetchHealth()
      } catch (err) {
        const detail = err.response?.data
        this.deviceSwitchError = detail?.message || err.message || 'Failed to switch device.'
        console.error('Device switch error:', this.deviceSwitchError)
      } finally {
        this.isSwitchingDevice = false
      }
    },

    async setFileAndInspect(file) {
      this.selectedFile = file
      this.isInspecting = true
      this.inspectError = null
      this.predictionResult = null

      try {
        const data = await inspectCsv(file)
        this.inspectionData = data

        // Pre-fill suggested configuration
        if (data.suggestions) {
          if (data.suggestions.recommended_task) {
            this.selectedTask = data.suggestions.recommended_task
          }
          if (data.suggestions.recommended_target) {
            this.selectedTarget = data.suggestions.recommended_target
          } else if (this.selectedTask !== 'anomaly' && data.columns.length > 0) {
            this.selectedTarget = data.columns[data.columns.length - 1].name
          }
          if (data.suggestions.recommended_time_column) {
            this.selectedTimeColumn = data.suggestions.recommended_time_column
          }
        }

        // Auto advance to Step 2
        this.currentStep = 2
      } catch (err) {
        const errorDetail = err.response?.data
        this.inspectError = {
          code: errorDetail?.error_code || 'INSPECTION_FAILED',
          message: errorDetail?.message || err.message || 'Failed to inspect dataset.',
          hint: errorDetail?.hint || 'Check if the file is a standard UTF-8 formatted CSV.',
        }
      } finally {
        this.isInspecting = false
      }
    },

    async executePrediction() {
      if (!this.isConfigValid) return

      this.currentStep = 3
      this.isPredicting = true
      this.predictError = null

      try {
        const result = await runPrediction({
          file: this.selectedFile,
          task: this.selectedTask,
          targetColumn: this.selectedTarget,
          timeColumn: this.selectedTimeColumn,
          horizon: this.forecastHorizon,
          autoSubsample: this.autoSubsample,
        })

        this.predictionResult = result
        this.currentStep = 4
      } catch (err) {
        const errorDetail = err.response?.data
        this.predictError = {
          code: errorDetail?.error_code || 'PREDICTION_FAILED',
          message: errorDetail?.message || err.message || 'Model prediction failed.',
          hint: errorDetail?.hint || 'Review your task selection and target column consistency.',
        }
        this.currentStep = 2 // return to config so user can adjust
      } finally {
        this.isPredicting = false
      }
    },

    resetAll() {
      this.currentStep = 1
      this.selectedFile = null
      this.inspectionData = null
      this.inspectError = null
      this.predictError = null
      this.predictionResult = null
      this.selectedTask = 'classification'
      this.selectedTarget = ''
      this.selectedTimeColumn = ''
    },

    goToStep(step) {
      if (step === 1) {
        this.currentStep = 1
      } else if (step === 2 && this.inspectionData) {
        this.currentStep = 2
      } else if (step === 4 && this.predictionResult) {
        this.currentStep = 4
      }
    },
  },
})
