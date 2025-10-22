import { useQuery } from "@tanstack/react-query"
import { useMemo } from "react"
import { API_URL } from "../api"
import { HuggingFaceModel, HuggingFaceModels } from "../types/huggingface"

async function fetchHuggingFaceModel(name: string): Promise<HuggingFaceModel> {
  const res = await fetch(`${API_URL}/model/${name}`, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  })
  const data = await res.json()
  return data
}

async function fetchHuggingFaceModels(owner: string): Promise<HuggingFaceModels> {
  const res = await fetch(`${API_URL}/models/${owner}`, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  })
  const data = await res.json()
  return data
}

export function useGetModel(name: string) {
  const { data, error, isFetching } = useQuery({
    queryKey: ["hf", "models", "get", name],
    queryFn: () => fetchHuggingFaceModel(name),
    // enabled: true,
  })

  const values = useMemo(() => {
    return { data, isFetching, error }
  }, [data, isFetching, error])

  return values
}

export function useListModels() {
  const { data, error, isFetching } = useQuery({
    queryKey: ["hf", "models", "list", "dataesr"],
    queryFn: () => fetchHuggingFaceModels("dataesr"),
    // enabled: true,
  })

  const values = useMemo(() => {
    return { data, isFetching, error }
  }, [data, isFetching, error])

  return values
}
