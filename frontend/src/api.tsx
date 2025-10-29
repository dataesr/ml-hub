import { transformJob } from "./pages/jobs/helpers"
import { HuggingFaceModel, HuggingFaceModels } from "./types/models"
import { OvhAiJob, OvhAiJobInputs, OvhAiJobs } from "./types/jobs"

export const API_URL = import.meta.env.VITE_API_URL || "/api"

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
  return await apiRequest(`${API_URL}/hf/dataset/${name}`, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  })
}

export async function apiDatasetsList(owner: string): Promise<any> {
  return await apiRequest(`${API_URL}/hf/datasets/${owner}`, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  })
}

/// HuggingFace Models
export async function apiModelsGet(name: string): Promise<HuggingFaceModel> {
  return await apiRequest(`${API_URL}/hf/model/${name}`, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  })
}

export async function apiModelsList(owner: string): Promise<HuggingFaceModels> {
  return await apiRequest(`${API_URL}/hf/models/${owner}`, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  })
}

/// OVHAI Jobs
export async function apiJobsGet(id: string): Promise<OvhAiJob> {
  const data = await apiRequest(`${API_URL}/ovhai/jobs/${id}`, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  })
  return transformJob(data)
}

export async function apiJobsList(state: string): Promise<OvhAiJobs> {
  const state_url = state ? `?state=${state}` : ""
  const data = await apiRequest(`${API_URL}/ovhai/jobs${state_url}`, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  })
  return Array.isArray(data) ? data.map(transformJob) : []
}

export async function apiJobsCreate(job: OvhAiJobInputs): Promise<OvhAiJob> {
  const data = await apiRequest(`${API_URL}/ovhai/jobs/finetuning`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(job),
  })
  return transformJob(data)
}

/// OVHAI deploys
