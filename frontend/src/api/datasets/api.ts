import { api } from "../client"
import { Dataset, DatasetConfig, DatasetConfigInfo } from "./types"

const API_DATASETS_URL = "/datasets"
const API_DATASETS_CONFIGS = "/configs"

export async function listDatasets(owner?: string): Promise<Dataset[]> {
  return api.get(`${API_DATASETS_URL}/${owner || ""}`)
}

export async function getDataset(name: string): Promise<Dataset> {
  return api.get(`${API_DATASETS_URL}/${name}`)
}

export async function listDatasetConfigs(dataset_name: string): Promise<DatasetConfigInfo[]> {
  return api.get(`${API_DATASETS_CONFIGS}?dataset_name=${dataset_name}`)
}

export async function getDatasetConfig(name: string, dataset_name: string): Promise<DatasetConfig> {
  return api.get(`${API_DATASETS_CONFIGS}/${name}?dataset_name=${dataset_name}`)
}

export async function addDatasetConfig(config: DatasetConfig): Promise<any> {
  return api.post(API_DATASETS_CONFIGS, config)
}
