import { useQuery } from "@tanstack/react-query"
import { useMemo } from "react"
import { apiDatasetsGet, apiDatasetsList } from "../api"

export function useGetDataset(name: string) {
  const { data, error, isFetching } = useQuery({
    queryKey: ["hf", "datasets", "get", name],
    queryFn: () => apiDatasetsGet(name),
    refetchOnWindowFocus: false,
    refetchOnMount: false,
    // staleTime: 5 * 60 * 1000,
  })

  const values = useMemo(() => {
    return { data, isFetching, error }
  }, [data, isFetching, error])

  return values
}

export function useListDatasets() {
  const { data, error, isFetching } = useQuery({
    queryKey: ["hf", "datasets", "list", "dataesr"],
    queryFn: () => apiDatasetsList("dataesr"),
    refetchOnWindowFocus: false,
    refetchOnMount: false,
    // staleTime: 5 * 60 * 1000,
  })

  const values = useMemo(() => {
    return { data, isFetching, error }
  }, [data, isFetching, error])

  return values
}
