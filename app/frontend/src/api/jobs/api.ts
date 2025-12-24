import { api } from "../client"
import { Job } from "./types"

const API_JOBS_URL = "/cloud/jobs"

function buildJob(data: any): Job {
  return {
    ...data,
    created_at: data.created_at ? new Date(data.created_at) : undefined,
    updated_at: data.updated_at ? new Date(data.updatedAt) : undefined,
    queued_at: data.queued_at ? new Date(data.queued_at) : undefined,
    started_at: data.started_at ? new Date(data.started_at) : undefined,
    stopped_at: data.stopped_at ? new Date(data.stopped_at) : undefined,
    finalized_at: data.finalized_at ? new Date(data.finalized_at) : undefined,
    duration: data.duration ? Number(data.duration) : undefined,
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

export async function stopJob(id: string): Promise<any> {
  api.post(`${API_JOBS_URL}/${id}/stop`)
}
