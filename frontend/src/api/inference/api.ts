import { api } from "../client"
import { InferenceApp, InferenceCompletions, InferenceInputs } from "./types"

const API_INFERENCE_URL = "/inference"

function buildApp(data: any): InferenceApp {
  return {
    ...data,
    createdAt: data.createdAt ? new Date(data.createdAt) : undefined,
    updatedAt: data.updatedAt ? new Date(data.updatedAt) : undefined,
  }
}

export async function getInferenceApp(id: string): Promise<InferenceApp> {
  const data = await api.get(`${API_INFERENCE_URL}/${id}`)
  return buildApp(data)
}

export async function listInferenceApps(state: string): Promise<InferenceApp[]> {
  const state_url = state ? `?state=${state}` : ""
  const data = await api.get(`${API_INFERENCE_URL}${state_url}`)
  return Array.isArray(data) ? data.map(buildApp) : []
}

// export async function createJob(app: InferenceAppInputs): Promise<InferenceApp> {
//   const data = await api.post(`${API_INFERENCE_URL}`, app)
//   return buildApp(data)
// }

export async function stopInferenceApp(id: string): Promise<any> {
  api.post(`${API_INFERENCE_URL}/${id}/stop`)
}

export async function startInferenceApp(id: string): Promise<any> {
  api.post(`${API_INFERENCE_URL}/${id}/start`)
}

export async function runInference(id: string, inputs: InferenceInputs): Promise<InferenceCompletions> {
  const data: InferenceCompletions = await api.post(`${API_INFERENCE_URL}/${id}/generate`, inputs)
  return data
}
