import { OvhAiJob } from "../../../types/jobs"

export function buildJob(data: any): OvhAiJob {
  return {
    ...data,
    createdAt: data.createdAt ? new Date(data.createdAt) : undefined,
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
