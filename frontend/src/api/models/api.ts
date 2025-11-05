import { api } from "../client"
import { Model } from "./types"

const API_MODELS_URL = "/models"

export async function getModel(name: string): Promise<Model> {
  return api.get(`${API_MODELS_URL}/${name}`)
}

export async function listModels(owner?: string): Promise<Model[]> {
  return api.get(`${API_MODELS_URL}/${owner || ""}`)
}
