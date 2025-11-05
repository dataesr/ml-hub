import { api } from "../client"
import { Dataset, DatasetConfig } from "./types"

const API_DATASETS_URL = "/datasets"
const API_DATASETS_CONFIGS = "/configs"

export async function listDatasets(owner?: string): Promise<Dataset[]> {
  return api.get(`${API_DATASETS_URL}/${owner || ""}`)
}

export async function getDataset(name: string): Promise<Dataset> {
  return api.get(`${API_DATASETS_URL}/${name}`)
}

export async function listDatasetConfig(): Promise<DatasetConfig> {
  return api.get(API_DATASETS_CONFIGS)
}

export async function getDatasetConfig(name: string): Promise<DatasetConfig> {
  return api.get(`${API_DATASETS_CONFIGS}/${name}`)
}

export async function addDatasetConfig(config: DatasetConfig): Promise<any> {
  return api.post(API_DATASETS_CONFIGS, config)
}
