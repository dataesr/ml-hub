import { api } from "../client"
import { Job, JobInputs } from "./types"

const API_JOBS_URL = "/jobs"

function buildJob(data: any): Job {
  return {
    ...data,
    createdAt: data.createdAt ? new Date(data.createdAt) : undefined,
    updatedAt: data.updatedAt ? new Date(data.updatedAt) : undefined,
    status: {
      ...data.status,
      duration: data.status?.duration ? Number(data.status.duration) : undefined,
      queuedAt: data.status?.queuedAt ? new Date(data.status.queuedAt) : undefined,
      startedAt: data.status?.startedAt ? new Date(data.status.startedAt) : undefined,
      finalizedAt: data.status?.finalizedAt ? new Date(data.status.finalizedAt) : undefined,
    },
  }
}

export async function getJob(id: string): Promise<Job> {
  const data = await api.get(`${API_JOBS_URL}/${id}`)
  return buildJob(data)
}

export async function listJobs(state: string): Promise<Job[]> {
  const state_url = state ? `?state=${state}` : ""
  const data = await api.get(`${API_JOBS_URL}${state_url}`)
  return Array.isArray(data) ? data.map(buildJob) : []
}

export async function createJob(job: JobInputs): Promise<Job> {
  const data = await api.post(API_JOBS_URL, job)
  return buildJob(data)
}

export async function stopJob(id: string): Promise<any> {
  api.post(`${API_JOBS_URL}/${id}/stop`)
}
