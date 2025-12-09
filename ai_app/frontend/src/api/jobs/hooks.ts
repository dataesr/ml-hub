import { useQuery } from "@tanstack/react-query"
import { useMemo } from "react"
import { getJob, listJobs } from "./api"
import { JobState } from "./types"

export function useGetJob(name: string) {
  const { data, error, isFetching } = useQuery({
    queryKey: ["jobs", "get", name],
    queryFn: () => getJob(name),
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

export function useListJobs(state: JobState = null) {
  const { data, error, isFetching, refetch } = useQuery({
    queryKey: ["jobs", "list", state || "all"],
    queryFn: () => listJobs(state),
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
