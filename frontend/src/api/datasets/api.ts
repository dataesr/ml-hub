import { api } from "../client"
import { Dataset, DatasetConfig } from "./types"

const API_DATASETS_URL = "/datasets"
const API_DATASETS_CONFIGS = API_DATASETS_URL + "/configs"

export async function listDatasets(owner?: string): Promise<Dataset[]> {
  return api.get(`${API_DATASETS_URL}/${owner || ""}`)
}

export async function getDataset(name: string): Promise<Dataset> {
  return api.get(`${API_DATASETS_URL}/${name}`)
}

export async function addDatasetConfig(config: DatasetConfig): Promise<any> {
  return api.post(API_DATASETS_CONFIGS, config)
}
