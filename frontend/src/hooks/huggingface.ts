import { useQuery } from "@tanstack/react-query"
import { useMemo } from "react"
import { fetchHuggingFaceModel, fetchHuggingFaceModels } from "../api"

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
