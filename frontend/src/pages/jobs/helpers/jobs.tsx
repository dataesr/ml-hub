import { ColorFamily } from "@dataesr/dsfr-plus"
import { OvhAiJob } from "../../../types/jobs"
import { OvhaiJobState } from "../../../types/jobs"

export const OVH_AI_TRAINING_URL = import.meta.env.VITE_OVH_AI_TRAINING_URL

export const getStateColor = (state: OvhaiJobState): ColorFamily => {
  switch (state) {
    case "DONE":
      return "green-emeraude"
    case "RUNNING":
    case "INITIALIZING":
    case "FINALIZING":
    case "PENDING":
      return "blue-cumulus"
    case "FAILED":
    case "ERROR":
    case "SYNC_FAILED":
    case "TIMEOUT":
      return "beige-gris-galet"
    case "INTERRUPTED":
    case "INTERRUPTING":
      return "orange-terre-battue"
    default:
      return "blue-cumulus"
  }
}

export function transformJob(data: any): OvhAiJob {
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
