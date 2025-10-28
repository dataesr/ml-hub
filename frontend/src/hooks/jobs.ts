import { useQuery } from "@tanstack/react-query"
import { useMemo } from "react"
import { apiJobsGet, apiJobsList } from "../api"
import { OvhaiJobState } from "../types/ovhai"

export function useGetJob(name: string) {
  const { data, error, isFetching } = useQuery({
    queryKey: ["ovhai", "jobs", "get", name],
    queryFn: () => apiJobsGet(name),
    // enabled: true,
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
    // enabled: true,
  })

  const values = useMemo(() => {
    return { data, isFetching, error }
  }, [data, isFetching, error])

  return values
}
