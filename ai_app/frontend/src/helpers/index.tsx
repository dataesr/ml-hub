import { getDataset } from "../api/datasets/api"
import { getModel } from "../api/models/api"

const hfGetMapping = {
  model: getModel,
  dataset: getDataset,
}
export async function hfGetRepository(name: string, type: "model" | "dataset") {
  const data = await hfGetMapping[type](name)
  return data
}
