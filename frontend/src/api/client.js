import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 600000, // 10 minutes timeout – matches Vite proxy for heavy TabPFN inference on CPU
})

export const getHealth = async () => {
  const response = await api.get('/health')
  return response.data
}

export const inspectCsv = async (file) => {
  const formData = new FormData()
  formData.append('file', file)
  const response = await api.post('/inspect', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}

export const runPrediction = async ({
  file,
  task,
  targetColumn,
  timeColumn,
  horizon,
  autoSubsample = true,
}) => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('task', task)
  if (targetColumn) {
    formData.append('target_column', targetColumn)
  }
  if (timeColumn) {
    formData.append('time_column', timeColumn)
  }
  if (horizon !== undefined && horizon !== null) {
    formData.append('horizon', String(horizon))
  }
  formData.append('auto_subsample', String(autoSubsample))

  const response = await api.post('/predict', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}

export const switchDevice = async (device) => {
  const response = await api.post('/device', { device })
  return response.data
}

export default api
