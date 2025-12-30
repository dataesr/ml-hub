import { Table } from "@codegouvfr/react-dsfr/Table"
import CopyToClipboard from "../../../components/copy-to-clipboard"
import { Badge, Button, ButtonGroup, Tag, Text } from "@dataesr/dsfr-plus"
import { formatDate, formatDuration } from "../../../utils"
import { getStateColor, getTaskColor } from "../helpers/colors"
import { Job } from "../../../api/jobs/types"

const TABLE_CONFIG = [
  { header: "Name / ID", component: "name" },
  { header: "Image", component: "image" },
  { header: "Status", component: "status" },
  { header: "Resources", component: "resources" },
  { header: "Started", component: "started_at" },
  { header: "Duration", component: "duration" },
  { header: "Actions", component: "actions" },
]

const buildTableComponents = (job: Job) => {
  const name = (
    <>
      <CopyToClipboard copyText={job.name}>
        <Text size="sm" bold>
          {job.name}
        </Text>
      </CopyToClipboard>
      <CopyToClipboard copyText={job.id}>
        <Text className="fr-text-mention--grey" size="sm">
          {job.id}
        </Text>
      </CopyToClipboard>
    </>
  )
  const image = <Badge color={getTaskColor(job.task)}>{job.task}</Badge>
  const status = <Tag color={getStateColor(job.state)}>{job.state}</Tag>
  const resources = job.resources?.gpu ? (
    <>
      <Text size="sm">GPU: {job.resources.gpu}</Text>
      <Text size="sm">{job.resources.gpuModel}</Text>
    </>
  ) : (
    <Text size="sm">CPU: {job.resources.cpu}</Text>
  )
  const started_at = job.started_at ? formatDate(job.started_at) : "-"
  const finalized_at = job.finalized_at ? formatDate(job.finalized_at) : "-"
  const duration = job.duration ? formatDuration(job.duration) : "-"

  const actions = (
    <ButtonGroup size="sm" isInlineFrom="xs">
      <Button size="sm" icon="external-link-line" variant="text" onClick={() => window.open(job.external_url, "_blank")}>
        Open
      </Button>
      {/* <Button size="sm" icon="delete-line" variant="text" onClick={() => alert("coucou")}>
        Delete
      </Button> */}
    </ButtonGroup>
  )

  return {
    name,
    image,
    status,
    resources,
    started_at,
    finalized_at,
    duration,
    actions,
  }
}

export default function JobsTable({ jobs }: { jobs: Job[] }) {
  const headers = TABLE_CONFIG.map((col) => col.header)
  const data = jobs.map((job) => buildTableComponents(job)).map((job) => TABLE_CONFIG.map((col) => job[col.component]))
  return <Table className="fr-pt-0" headers={headers} data={data} />
}
