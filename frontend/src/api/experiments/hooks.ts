import { useQuery } from "@tanstack/react-query"
import { useMemo } from "react"
import {
  getExperimentArtifact,
  getExperimentsRun,
  listExperiments,
  listExperimentsArtifacts,
  listExperimentsRuns,
} from "./api"
import { ExperimentArtifactKind } from "./types"

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

export function useGetRun(project: string, id: string) {
  const { data, error, isFetching } = useQuery({
    queryKey: ["experiments", "runs", "get", project, id],
    queryFn: () => getExperimentsRun(project, id),
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
    queryKey: ["experiments", "runs", "list", project],
    queryFn: () => listExperimentsRuns(project),
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

export function useGetArtifact<K extends ExperimentArtifactKind>(
  project: string,
  name: string,
  type: ExperimentArtifactKind
) {
  const { data, error, isFetching } = useQuery({
    queryKey: ["experiments", "artifacts", "get", project, name, type],
    queryFn: () => getExperimentArtifact<K>(project, name, type),
    refetchOnWindowFocus: false,
    refetchOnMount: false,
    // staleTime: 5 * 60 * 1000,
  })

  const values = useMemo(() => {
    return { data, isFetching, error }
  }, [data, isFetching, error])

  return values
}

export function useListArtifacts(project: string, type: ExperimentArtifactKind) {
  const { data, error, isFetching } = useQuery({
    queryKey: ["experiments", "artifacts", "list", project],
    queryFn: () => listExperimentsArtifacts(project, type),
    refetchOnWindowFocus: false,
    refetchOnMount: false,
    // staleTime: 5 * 60 * 1000,
  })

  const values = useMemo(() => {
    return { data, isFetching, error }
  }, [data, isFetching, error])

  return values
}
