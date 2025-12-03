import { useQuery } from "@tanstack/react-query"
import { useMemo } from "react"
import { getInferenceApp, listInferenceApps } from "./api"
import { InferenceAppState } from "./types"

export function useGetApp(name: string) {
  const { data, error, isFetching } = useQuery({
    queryKey: ["jobs", "get", name],
    queryFn: () => getInferenceApp(name),
    refetchOnWindowFocus: false,
    refetchOnMount: false,
    keepPreviousData: true,
    // staleTime: 5 * 60 * 1000,
  })

  const values = useMemo(() => {
    return { data, isFetching, error }
  }, [data, isFetching, error])

  return values
}

export function useListApps(state: InferenceAppState = null) {
  const { data, error, isFetching, refetch } = useQuery({
    queryKey: ["apps", "list", state || "all"],
    queryFn: () => listInferenceApps(state),
    refetchOnWindowFocus: false,
    refetchOnMount: true,
    keepPreviousData: true,
    // staleTime: 5 * 60 * 1000,
  })

  const values = useMemo(() => {
    return { data, isFetching, error, refetch }
  }, [data, isFetching, error, refetch])

  return values
}
