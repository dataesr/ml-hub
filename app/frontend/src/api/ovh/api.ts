import { api } from "../client"
import { OVHJob } from "./types"

const API_OVH_JOBS_URL = "/ovh/jobs"

function buildOVHJob(data: any): OVHJob {
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

export async function getOVHJob(id: string): Promise<OVHJob> {
  const data = await api.get(`${API_OVH_JOBS_URL}/${id}`)
  return buildOVHJob(data)
}

export async function listOVHJobs(state: string): Promise<OVHJob[]> {
  const state_url = state ? `?state=${state}` : ""
  const data = await api.get(`${API_OVH_JOBS_URL}${state_url}`)
  return Array.isArray(data) ? data.map(buildOVHJob) : []
}

export async function stopOVHJob(id: string): Promise<any> {
  api.post(`${API_OVH_JOBS_URL}/${id}/stop`)
}
