import { useQuery, useMutation } from "@tanstack/react-query"
import { useMemo } from "react"
import { listPipelines, getPipeline, runPipeline } from "./api"

export function useListPipelines() {
  const { data, error, isFetching } = useQuery({
    queryKey: ["pipelines", "list"],
    queryFn: () => listPipelines(),
    refetchOnWindowFocus: false,
    refetchOnMount: false,
  })

  const values = useMemo(() => {
    return { data, isFetching, error }
  }, [data, isFetching, error])

  return values
}

export function useGetPipeline(name: string) {
  const { data, error, isFetching } = useQuery({
    queryKey: ["pipelines", "get", name],
    queryFn: () => getPipeline(name),
    enabled: !!name,
    refetchOnWindowFocus: false,
    refetchOnMount: false,
  })

  const values = useMemo(() => {
    return { data, isFetching, error }
  }, [data, isFetching, error])

  return values
}

export function useRunPipeline() {
  return useMutation({
    mutationFn: ({ name, data }: { name: string; data: any }) => runPipeline(name, data),
  })
}
