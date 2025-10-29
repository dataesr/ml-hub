import { apiDatasetsGet, apiModelsGet } from "../api"

const hfGetMapping = {
  model: apiModelsGet,
  dataset: apiDatasetsGet,
}
export async function hfGetRepository(name: string, type: "model" | "dataset") {
  const data = await hfGetMapping[type](name)
  return data
}
