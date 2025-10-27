import { Tag, TagGroup, Link, Container, ColorFamily } from "@dataesr/dsfr-plus"
import { Card } from "@codegouvfr/react-dsfr/Card"
import { OvhAiJob, OvhaiJobState } from "../types/ovhai"

type JobCardProps = {
  job: OvhAiJob
}

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

const formatDate = (date: Date | string): string => {
  const d = typeof date === "string" ? new Date(date) : date
  return d.toLocaleString("fr-FR", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  })
}

export default function JobCard({ job }: JobCardProps) {
  return (
    <Container className="fr-card fr-mb-2w">
      <Card
        title={job.spec.name || job.id}
        horizontal
        start={
          <div>
            <TagGroup className="fr-mb-2w">
              <Tag color={getStateColor(job.status.state)}>{job.status.state}</Tag>
              {job.spec.resources.gpu && <Tag color="blue-cumulus">GPU: {job.spec.resources.gpu}</Tag>}
              {job.spec.resources.cpu && <Tag color="blue-cumulus">CPU: {job.spec.resources.cpu}</Tag>}
            </TagGroup>
            <div style={{ fontSize: "0.875rem", color: "#666" }}>
              <div>
                <strong>Image:</strong> {job.spec.image}
              </div>
              {job.status.duration && (
                <div>
                  <strong>Duration:</strong> {job.status.duration}
                </div>
              )}
              {job.status.startedAt && (
                <div>
                  <strong>Started:</strong> {formatDate(job.status.startedAt)}
                </div>
              )}
            </div>
          </div>
        }
        footer={
          job.status.url ? (
            <Link icon="external-link-line" iconPosition="right" href={job.status.url} target="_blank">
              Open job
            </Link>
          ) : null
        }
        linkProps={
          job.status.state === "RUNNING" || job.status.state === "QUEUED" || job.status.state === "PENDING" ? {} : undefined
        }
      />
    </Container>
  )
}
