import { useQuery } from "@tanstack/react-query"
import { useMemo } from "react"
import { getDataset, getDatasetConfig, listDatasetConfigs, listDatasets } from "./api"

export function useGetDataset(name: string) {
  const { data, error, isFetching } = useQuery({
    queryKey: ["datasets", "get", name],
    queryFn: () => getDataset(name),
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
    queryKey: ["datasets", "list"],
    queryFn: () => listDatasets(),
    refetchOnWindowFocus: false,
    refetchOnMount: false,
    // staleTime: 5 * 60 * 1000,
  })

  const values = useMemo(() => {
    return { data, isFetching, error }
  }, [data, isFetching, error])

  return values
}

export function useListDatasetConfigs(dataset_name: string) {
  const { data, error, isFetching } = useQuery({
    queryKey: ["datasets", "list", "configs", dataset_name],
    queryFn: () => listDatasetConfigs(dataset_name),
    refetchOnWindowFocus: false,
    refetchOnMount: false,
    enabled: Boolean(dataset_name.length),
    // staleTime: 5 * 60 * 1000,
  })

  const values = useMemo(() => {
    return { data, isFetching, error }
  }, [data, isFetching, error])

  return values
}

export function useGetDatasetConfig(name: string, dataset_name: string) {
  const { data, error, isFetching } = useQuery({
    queryKey: ["datasets", "get", "config", name, dataset_name],
    queryFn: () => getDatasetConfig(name, dataset_name),
    refetchOnWindowFocus: false,
    refetchOnMount: false,
    enabled: Boolean(name && dataset_name.length),
    // staleTime: 5 * 60 * 1000,
  })

  const values = useMemo(() => {
    return { data, isFetching, error }
  }, [data, isFetching, error])

  return values
}
