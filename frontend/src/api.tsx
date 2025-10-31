import { buildJob } from "./pages/jobs/helpers/build"
import { HuggingFaceModel } from "./types/models"
import { OvhAiJob, OvhAiJobInputs } from "./types/jobs"
import { ArtifactKind, WandbArtifact, WandbProject, WandbRun } from "./types/experiments"
import { buildArtifact, buildProject, buildRun } from "./pages/experiments/helpers/build"
import { HuggingFaceDataset } from "./types/datasets"

export const HUGGING_FACE_URL = "https://huggingface.co"
export const OVHAI_TRAINING_URL = import.meta.env.VITE_OVHAI_TRAINING_URL

export const API_URL = import.meta.env.VITE_API_URL || "/api"
const API_DATASETS_URL = API_URL + "/hf/datasets"
const API_MODELS_URL = API_URL + "/hf/models"
const API_JOBS_URL = API_URL + "/ovhai/jobs"
const API_EXPERIMENTS_URL = API_URL + "/wandb/projects"
const API_RUNS_URL = API_URL + "/wandb/runs"
const API_ARTIFACTS_URL = API_URL + "/wandb/artifacts"

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
export async function apiDatasetsGet(name: string): Promise<HuggingFaceDataset> {
  return await apiRequest(`${API_DATASETS_URL}/${name}`, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  })
}

export async function apiDatasetsList(owner: string): Promise<HuggingFaceDataset[]> {
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

export async function apiModelsList(owner: string): Promise<HuggingFaceModel[]> {
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
  return buildJob(data)
}

export async function apiJobsList(state: string): Promise<OvhAiJob[]> {
  const state_url = state ? `?state=${state}` : ""
  const data = await apiRequest(`${API_JOBS_URL}${state_url}`, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  })
  return Array.isArray(data) ? data.map(buildJob) : []
}

export async function apiJobsCreate(job: OvhAiJobInputs, jobType: string = "finetuning"): Promise<OvhAiJob> {
  const data = await apiRequest(`${API_JOBS_URL}/${jobType}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(job),
  })
  return buildJob(data)
}

/// OVHAI deploys

/// Weights & Biases
export async function apiExperimentsList(entity: string): Promise<WandbProject[]> {
  const data = await apiRequest(`${API_EXPERIMENTS_URL}/${entity}`, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  })
  return Array.isArray(data) ? data.map(buildProject) : []
}

export async function apiRunsList(entity: string, project: string): Promise<WandbRun[]> {
  const data = await apiRequest(`${API_RUNS_URL}/${entity}/${project}`, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  })
  return Array.isArray(data) ? data.map(buildRun) : []
}

export async function apiRunsGet(entity: string, project: string, id: string): Promise<WandbRun> {
  const data = await apiRequest(`${API_RUNS_URL}/${entity}/${project}/${id}`, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  })
  return buildRun(data)
}

export async function apiArtifactsGet<K extends ArtifactKind>(
  entity: string,
  project: string,
  name: string,
  type: ArtifactKind
): Promise<WandbArtifact<K>> {
  const data = await apiRequest(`${API_ARTIFACTS_URL}/${entity}/${project}/${name}?type=${type}`, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  })
  return buildArtifact(data) as WandbArtifact<K>
}
export async function apiArtifactsList<K extends ArtifactKind>(
  entity: string,
  project: string,
  type: K
): Promise<Array<WandbArtifact<K>>> {
  const data = await apiRequest(`${API_ARTIFACTS_URL}/${entity}/${project}?type=${type}`, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  })
  return (Array.isArray(data) ? data.map(buildArtifact) : []) as Array<WandbArtifact<K>>
}
