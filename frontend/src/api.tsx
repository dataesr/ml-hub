import { transformJob } from "./pages/jobs/helpers/jobs"
import { HuggingFaceModel, HuggingFaceModels } from "./types/huggingface"
import { OvhAiJob, OvhAiJobs } from "./types/ovhai"

export const API_URL = import.meta.env.VITE_API_URL

/// HuggingFace Models
export async function apiModelsGet(name: string): Promise<HuggingFaceModel> {
  const res = await fetch(`${API_URL}/model/${name}`, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  })
  const data = await res.json()
  return data
}

export async function apiModelsList(owner: string): Promise<HuggingFaceModels> {
  const res = await fetch(`${API_URL}/models/${owner}`, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  })
  const data = await res.json()
  return data
}

/// OVHAI
export async function apiJobsGet(id: string): Promise<OvhAiJob> {
  const res = await fetch(`${API_URL}/ovhai/jobs/${id}`, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  })
  const data = await res.json()
  return transformJob(data)
}

export async function apiJobsList(state: string): Promise<OvhAiJobs> {
  const state_url = state ? `?state=${state}` : ""
  const res = await fetch(`${API_URL}/ovhai/jobs${state_url}`, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  })
  const data = await res.json()
  return Array.isArray(data) ? data.map(transformJob) : []
}

export async function apiJobsCreate(job: Record<string, any>): Promise<OvhAiJob> {
  const res = await fetch(`${API_URL}/ovhai/jobs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(job),
  })
  const data = await res.json()
  return transformJob(data)
}
