import { useQuery } from "@tanstack/react-query"
import { useMemo } from "react"
import { getDataset, listDatasets } from "./api"

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
