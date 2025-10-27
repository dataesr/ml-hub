import { useQuery } from "@tanstack/react-query"
import { useMemo } from "react"
import { API_URL } from "../api"
import { OvhAiJob, OvhAiJobs, OvhaiJobState } from "../types/ovhai"

function transformJob(data: any): OvhAiJob {
  return {
    ...data,
    createdAt: data.createdAt ? new Date(data.createdAt) : new Date(),
    updatedAt: data.updatedAt ? new Date(data.updatedAt) : undefined,
    status: {
      ...data.status,
      duration: data.status?.duration ? Number(data.status.duration) : undefined,
      queuedAt: data.status?.queuedAt ? new Date(data.status.queuedAt) : undefined,
      startedAt: data.status?.startedAt ? new Date(data.status.startedAt) : undefined,
      finalizedAt: data.status?.finalizedAt ? new Date(data.status.finalizedAt) : undefined,
    },
  }
}

async function fetchOvhAiJob(id: string): Promise<OvhAiJob> {
  const res = await fetch(`${API_URL}/ovhai/jobs/${id}`, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  })
  const data = await res.json()
  return transformJob(data)
}

async function fetchOvhAiJobs(state: string): Promise<OvhAiJobs> {
  const state_url = state ? `?state=${state}` : ""
  const res = await fetch(`${API_URL}/ovhai/jobs${state_url}`, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  })
  const data = await res.json()
  return Array.isArray(data) ? data.map(transformJob) : []
}

export function useGetJob(name: string) {
  const { data, error, isFetching } = useQuery({
    queryKey: ["ovhai", "jobs", "get", name],
    queryFn: () => fetchOvhAiJob(name),
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
    queryFn: () => fetchOvhAiJobs(state),
    // enabled: true,
  })

  const values = useMemo(() => {
    return { data, isFetching, error }
  }, [data, isFetching, error])

  return values
}
