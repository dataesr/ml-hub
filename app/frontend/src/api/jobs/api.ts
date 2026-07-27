import { api } from "../client"
import { Job } from "./types"

const API_JOBS_URL = "/jobs"

export async function listJobs(): Promise<Job[]> {
  const pipelines = await api.get<Job[]>(API_JOBS_URL)
  return pipelines.map((p) => ({ ...p }))
}

export async function getJob(name: string): Promise<Job> {
  return api.get(`${API_JOBS_URL}/${name}`)
}

export async function runJob(name: string, data: any): Promise<any> {
  return api.post(`${API_JOBS_URL}/${name}/run`, data)
}
