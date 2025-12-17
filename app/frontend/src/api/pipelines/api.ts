import { api } from "../client"
import { Pipeline } from "./types"

const API_PIPELINES_URL = "/pipelines"

export async function listPipelines(): Promise<Pipeline[]> {
  const pipelines = await api.get<Pipeline[]>(API_PIPELINES_URL)
  return pipelines.map((p) => ({ ...p, id: p.name }))
}

export async function getPipeline(name: string): Promise<Pipeline> {
  return api.get(`${API_PIPELINES_URL}/${name}`)
}

export async function runPipeline(name: string, data: any): Promise<any> {
  return api.post(`${API_PIPELINES_URL}/${name}/run`, data)
}
