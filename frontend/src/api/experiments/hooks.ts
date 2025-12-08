import { useQuery } from "@tanstack/react-query"
import { useMemo } from "react"
import { getExperiment, getExperimentsRun, listExperiments, listExperimentsRuns } from "./api"

export function useListExperiments() {
  const { data, error, isFetching } = useQuery({
    queryKey: ["experiments", "list"],
    queryFn: () => listExperiments(),
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

export function useGetExperiment(id: string) {
  const { data, error, isFetching } = useQuery({
    queryKey: ["experiments", "get", id],
    queryFn: () => getExperiment(id),
    refetchOnWindowFocus: false,
    refetchOnMount: true,
    // keepPreviousData: true,
    // staleTime: 5 * 60 * 1000,
  })

  const values = useMemo(() => {
    return { data, isFetching, error }
  }, [data, isFetching, error])

  return values
}

export function useGetRun(run_id: string) {
  const { data, error, isFetching } = useQuery({
    queryKey: ["experiments", "runs", "get", run_id],
    queryFn: () => getExperimentsRun(run_id),
    refetchOnWindowFocus: false,
    refetchOnMount: false,
    // staleTime: 5 * 60 * 1000,
  })

  const values = useMemo(() => {
    return { data, isFetching, error }
  }, [data, isFetching, error])

  return values
}

export function useListRuns(id: string) {
  const { data, error, isFetching } = useQuery({
    queryKey: ["experiments", "runs", "list", id],
    queryFn: () => listExperimentsRuns(id),
    refetchOnWindowFocus: false,
    refetchOnMount: true,
    keepPreviousData: true,
    // staleTime: 5 * 60 * 1000,
  })

  const values = useMemo(() => {
    return { data, isFetching, error }
  }, [data, isFetching, error])

  return values
}