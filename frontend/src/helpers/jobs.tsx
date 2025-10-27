import { Button, ColorFamily, Tag, Text } from "@dataesr/dsfr-plus"
import { OvhAiJob } from "../types/ovhai"
import { OvhaiJobState } from "../types/ovhai"
import { formatDate, formatDuration } from "../utils"

const ovhAiTrainingUrl = import.meta.env.VITE_OVH_AI_TRAINING_URL

const getStateColor = (state: OvhaiJobState): ColorFamily => {
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

export const buildTableComponents = (job: OvhAiJob) => {
  const name = (
    <>
      <Text
        size="sm"
        bold
        onClick={() => {
          navigator.clipboard.writeText(job.spec.name)
        }}
        style={{ cursor: "pointer" }}
      >
        {job.spec.name}
      </Text>
      <Text
        className="fr-text-mention--grey"
        size="sm"
        onClick={() => {
          navigator.clipboard.writeText(job.spec.name)
        }}
        style={{ cursor: "pointer" }}
      >
        {job.id}
      </Text>
    </>
  )
  const status = <Tag color={getStateColor(job.status.state)}>{job.status.state}</Tag>
  const resources = job.spec.resources.gpu ? (
    <>
      <Text size="sm">GPU: {job.spec.resources.gpu}</Text>
      <Text size="sm">{job.spec.resources.gpuModel}</Text>
    </>
  ) : (
    <Text size="sm">CPU: {job.spec.resources.cpu}</Text>
  )
  const startedAt = job.status.startedAt ? formatDate(job.status.startedAt) : "-"
  const finalizedAt = job.status.finalizedAt ? formatDate(job.status.finalizedAt) : "-"
  const duration = job.status.duration ? formatDuration(job.status.duration) : "-"

  const actions = (
    <Button icon="external-link-line" size="sm" onClick={() => window.open(`${ovhAiTrainingUrl}/${job.id}`, "_blank")}>
      Open
    </Button>
  )

  return {
    name,
    status,
    resources,
    startedAt,
    finalizedAt,
    duration,
    actions,
  }
}
