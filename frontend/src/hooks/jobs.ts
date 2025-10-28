import { useQuery } from "@tanstack/react-query"
import { useMemo } from "react"
import { apiJobsGet, apiJobsList } from "../api"
import { OvhaiJobState } from "../types/jobs"

export function useGetJob(name: string) {
  const { data, error, isFetching } = useQuery({
    queryKey: ["ovhai", "jobs", "get", name],
    queryFn: () => apiJobsGet(name),
    refetchOnWindowFocus: false,
    refetchOnMount: false,
    // staleTime: 5 * 60 * 1000,
  })

  const values = useMemo(() => {
    return { data, isFetching, error }
  }, [data, isFetching, error])

  return values
}

export function useListJobs(state: OvhaiJobState = null) {
  const { data, error, isFetching } = useQuery({
    queryKey: ["ovhai", "jobs", "list", state || "all"],
    queryFn: () => apiJobsList(state),
    refetchOnWindowFocus: false,
    refetchOnMount: false,
    // staleTime: 5 * 60 * 1000,
  })

  const values = useMemo(() => {
    return { data, isFetching, error }
  }, [data, isFetching, error])

  return values
}
