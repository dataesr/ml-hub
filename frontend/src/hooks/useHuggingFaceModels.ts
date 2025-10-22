import { useQuery } from "@tanstack/react-query"
import { HuggingFaceModels } from "../types/huggingface"
import { useMemo } from "react"
import * as hub from "@huggingface/hub"

async function fetchHuggingFaceModels(owner?: string): Promise<HuggingFaceModels> {
  const models = []
  for await (const model of hub.listModels({
    search: { owner: owner },
    additionalFields: ["tags", "config"],
    accessToken: import.meta.env.VITE_HF_TOKEN,
  }))
    models.push(model)
  if (!Array.isArray(models)) return []
  return models as HuggingFaceModels
}

export function useHuggingFaceModels() {
  const { data, error, isFetching } = useQuery({
    queryKey: ["hf", "models", "dataesr"],
    queryFn: () => fetchHuggingFaceModels("dataesr"),
    // enabled: true,
  })

  const values = useMemo(() => {
    return { data, isFetching, error }
  }, [data, isFetching, error])

  return values
}
