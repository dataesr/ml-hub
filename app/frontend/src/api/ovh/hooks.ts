import { useQuery } from "@tanstack/react-query"
import { useMemo } from "react"
import { getOVHJob, listOVHJobs } from "./api"
import { OVHJobState } from "./types"

export function useGetOVHJob(name: string) {
  const { data, error, isFetching } = useQuery({
    queryKey: ["ovh", "jobs", "get", name],
    queryFn: () => getOVHJob(name),
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

export function useListOVHJobs(state: OVHJobState = null) {
  const { data, error, isFetching, refetch } = useQuery({
    queryKey: ["ovh", "jobs", "list", state || "all"],
    queryFn: () => listOVHJobs(state),
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
