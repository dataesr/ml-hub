import { Button, ColorFamily, Tag, Text } from "@dataesr/dsfr-plus"
import { OvhAiJob } from "../types/ovhai"
import { OvhaiJobState } from "../types/ovhai"
import { formatDate, formatDuration } from "../utils"

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

export const buildTableComponents = (job: OvhAiJob) => {
  const name = (
    <>
      <Text size="sm" bold>
        {job.spec.name}
      </Text>
      <Text className="fr-text-mention--grey" size="sm">
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
    <Button icon="external-link-line" size="sm" onClick={() => window.open(job.status.url, "_blank")}>
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
