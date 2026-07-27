import { useQuery, useMutation } from "@tanstack/react-query"
import { useMemo } from "react"
import { listJobs, getJob, runJob } from "./api"

export function useListJobs() {
  const { data, error, isFetching } = useQuery({
    queryKey: ["jobs", "list"],
    queryFn: () => listJobs(),
    refetchOnWindowFocus: false,
    refetchOnMount: false,
  })

  const values = useMemo(() => {
    return { data, isFetching, error }
  }, [data, isFetching, error])

  return values
}

export function useGetJob(name: string) {
  const { data, error, isFetching } = useQuery({
    queryKey: ["job", "get", name],
    queryFn: () => getJob(name),
    enabled: !!name,
    refetchOnWindowFocus: false,
    refetchOnMount: false,
  })

  const values = useMemo(() => {
    return { data, isFetching, error }
  }, [data, isFetching, error])

  return values
}

export function useRunJob() {
  return useMutation({
    mutationFn: ({ name, data }: { name: string; data: any }) => runJob(name, data),
  })
}
