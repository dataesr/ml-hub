import { useQuery } from "@tanstack/react-query"
import { useMemo } from "react"
import { apiArtifactsGet, apiArtifactsList, apiExperimentsList, apiRunsGet, apiRunsList } from "../api"
import { ArtifactKind } from "../types/experiments"

export function useListExperiments() {
  const { data, error, isFetching } = useQuery({
    queryKey: ["wandb", "projects", "list", "dataesr"],
    queryFn: () => apiExperimentsList("dataesr"),
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

export function useGetRun(project: string, id: string) {
  const { data, error, isFetching } = useQuery({
    queryKey: ["wandb", "runs", "get", "dataesr", project, id],
    queryFn: () => apiRunsGet("dataesr", project, id),
    refetchOnWindowFocus: false,
    refetchOnMount: false,
    // staleTime: 5 * 60 * 1000,
  })

  const values = useMemo(() => {
    return { data, isFetching, error }
  }, [data, isFetching, error])

  return values
}

export function useListRuns(project: string) {
  const { data, error, isFetching } = useQuery({
    queryKey: ["wandb", "runs", "list", "dataesr", project],
    queryFn: () => apiRunsList("dataesr", project),
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

export function useGetArtifact<K extends ArtifactKind>(project: string, name: string, type: ArtifactKind) {
  const { data, error, isFetching } = useQuery({
    queryKey: ["wandb", "artifacts", "get", "dataesr", project, name, type],
    queryFn: () => apiArtifactsGet<K>("dataesr", project, name, type),
    refetchOnWindowFocus: false,
    refetchOnMount: false,
    // staleTime: 5 * 60 * 1000,
  })

  const values = useMemo(() => {
    return { data, isFetching, error }
  }, [data, isFetching, error])

  return values
}

export function useListArtifacts(project: string, type: ArtifactKind) {
  const { data, error, isFetching } = useQuery({
    queryKey: ["wandb", "artifacts", "list", "dataesr", project],
    queryFn: () => apiArtifactsList("dataesr", project, type),
    refetchOnWindowFocus: false,
    refetchOnMount: false,
    // staleTime: 5 * 60 * 1000,
  })

  const values = useMemo(() => {
    return { data, isFetching, error }
  }, [data, isFetching, error])

  return values
}
