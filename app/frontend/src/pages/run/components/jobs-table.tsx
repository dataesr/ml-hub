import { Table } from "@codegouvfr/react-dsfr/Table"
import CopyToClipboard from "../../../components/copy-to-clipboard"
import { Badge, Button, Tag, TagGroup, Text } from "@dataesr/dsfr-plus"
import { Job } from "../../../api/jobs/types"
import { getEnvironmentColor } from "../helpers/colors"

const TABLE_CONFIG = [
  { header: "Name", component: "name" },
  { header: "Description", component: "description" },
  { header: "Environment", component: "environment" },
  { header: "Tags", component: "tags" },
  { header: "Actions", component: "actions" },
]

const buildTableComponents = (job: Job, onSelect: (job: string) => void) => {
  const name = (
    <CopyToClipboard copyText={job.name}>
      <Text size="sm" bold>
        {job.name}
      </Text>
    </CopyToClipboard>
  )
  const description = <Text size="xs">{job?.description || "-"}</Text>
  const environment = job?.ovh ? <Badge color={getEnvironmentColor("ovh")}>{"ovh"}</Badge> : "-"
  const tags = job?.tags ? (
    <TagGroup>
      {job.tags.map((tag) => (
        <Tag size="sm">{tag}</Tag>
      ))}
    </TagGroup>
  ) : (
    "-"
  )

  const actions = (
    <Button icon="play-line" size="sm" variant="text" onClick={() => onSelect(job.name)}>
      Run
    </Button>
  )

  return {
    name,
    description,
    environment,
    tags,
    actions,
  }
}

interface JobsTableProps {
  jobs: Job[]
  onSelect: (job: string) => void
}

export default function JobsTable({ jobs, onSelect }: JobsTableProps) {
  const headers = TABLE_CONFIG.map((col) => col.header)
  const data = jobs
    .map((job) => buildTableComponents(job, onSelect))
    .map((comp) => TABLE_CONFIG.map((col) => comp[col.component]))
  return <Table className="fr-pt-0" headers={headers} data={data} />
}
