import { api } from "../client"
import { Configs, JobConfig } from "./types"

const API_CONFIGS_URL = "/configs"

export async function listConfigs(): Promise<Configs> {
  return api.get(`${API_CONFIGS_URL}?data=true`)
}

export async function getConfig(name: string): Promise<JobConfig> {
  return api.get(`${API_CONFIGS_URL}/${name}`)
}