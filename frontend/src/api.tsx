import { transformJob } from "./pages/jobs/helpers"
import { HuggingFaceModel, HuggingFaceModels } from "./types/models"
import { OvhAiJob, OvhAiJobInputs, OvhAiJobs } from "./types/jobs"

export const HUGGING_FACE_URL = "https://huggingface.co"
export const OVHAI_TRAINING_URL = import.meta.env.VITE_OVHAI_TRAINING_URL

export const API_URL = import.meta.env.VITE_API_URL || "/api"
const API_DATASETS_URL = API_URL + "/hf/datasets"
const API_MODELS_URL = API_URL + "/hf/models"
const API_JOBS_URL = API_URL + "/ovhai/jobs"

async function apiRequest(input: RequestInfo | URL, init?: RequestInit) {
  try {
    const response = await fetch(input, init)
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${await response.text()}`)
    }
    const data = await response.json()
    return data
  } catch (error: any) {
    throw new Error(error?.message || "Network error")
  }
}

/// HuggingFace Dataset
export async function apiDatasetsGet(name: string): Promise<any> {
  return await apiRequest(`${API_DATASETS_URL}/${name}`, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  })
}

export async function apiDatasetsList(owner: string): Promise<any> {
  return await apiRequest(`${API_DATASETS_URL}?owner=${owner}`, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  })
}

/// HuggingFace Models
export async function apiModelsGet(name: string): Promise<HuggingFaceModel> {
  return await apiRequest(`${API_MODELS_URL}/${name}`, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  })
}

export async function apiModelsList(owner: string): Promise<HuggingFaceModels> {
  return await apiRequest(`${API_MODELS_URL}?owner=${owner}`, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  })
}

/// OVHAI Jobs
export async function apiJobsGet(id: string): Promise<OvhAiJob> {
  const data = await apiRequest(`${API_JOBS_URL}/${id}`, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  })
  return transformJob(data)
}

export async function apiJobsList(state: string): Promise<OvhAiJobs> {
  const state_url = state ? `?state=${state}` : ""
  const data = await apiRequest(`${API_JOBS_URL}${state_url}`, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  })
  return Array.isArray(data) ? data.map(transformJob) : []
}

export async function apiJobsCreate(job: OvhAiJobInputs, jobType: string = "finetuning"): Promise<OvhAiJob> {
  const data = await apiRequest(`${API_JOBS_URL}/${jobType}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(job),
  })
  return transformJob(data)
}

/// OVHAI deploys

/// Weights & Biases
// export async function apiExperimentsGet(object: ): Promise<any> {
  
// }
