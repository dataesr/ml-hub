import { Table } from "@codegouvfr/react-dsfr/Table"
import { OvhAiJob, OvhAiJobs } from "../../../types/jobs"
import CopyToClipboard from "../../../components/copy-to-clipboard"
import { Button, Tag, Text } from "@dataesr/dsfr-plus"
import { formatDate, formatDuration } from "../../../utils"
import { getStateColor, OVH_AI_TRAINING_URL } from "../helpers"

const TABLE_CONFIG = [
  { header: "Name / ID", component: "name" },
  { header: "Status", component: "status" },
  { header: "Resources", component: "resources" },
  { header: "Started", component: "startedAt" },
  { header: "Duration", component: "duration" },
  { header: "Actions", component: "actions" },
]

const buildTableComponents = (job: OvhAiJob) => {
  const name = (
    <>
      <CopyToClipboard copyText={job.spec.name}>
        <Text size="sm" bold>
          {job.spec.name}
        </Text>
      </CopyToClipboard>
      <CopyToClipboard copyText={job.id}>
        <Text className="fr-text-mention--grey" size="sm">
          {job.id}
        </Text>
      </CopyToClipboard>
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
    <Button
      icon="external-link-line"
      size="sm"
      variant="text"
      onClick={() => window.open(`${OVH_AI_TRAINING_URL}/${job.id}`, "_blank")}
    >
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

export default function JobsTable({ jobs }: { jobs: OvhAiJobs }) {
  const headers = TABLE_CONFIG.map((col) => col.header)
  const data = jobs.map((job) => buildTableComponents(job)).map((job) => TABLE_CONFIG.map((col) => job[col.component]))
  return <Table className="fr-pt-0" headers={headers} data={data} />
}
