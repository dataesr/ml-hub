import { Table } from "@codegouvfr/react-dsfr/Table"
import CopyToClipboard from "../../../components/copy-to-clipboard"
import { Badge, Button, Tag, TagGroup, Text } from "@dataesr/dsfr-plus"
import { Pipeline } from "../../../api/pipelines/types"
import { getEnvironmentColor } from "../helpers/colors"

const TABLE_CONFIG = [
  { header: "Name", component: "name" },
  { header: "Description", component: "description" },
  { header: "Environment", component: "environment" },
  { header: "Tags", component: "tags" },
  { header: "Actions", component: "actions" },
]

const buildTableComponents = (pipeline: Pipeline, onSelect: (pipeline: string) => void) => {
  const name = (
    <CopyToClipboard copyText={pipeline.pipeline}>
      <Text size="sm" bold>
        {pipeline.pipeline}
      </Text>
    </CopyToClipboard>
  )
  const description = <Text size="xs">{pipeline?.description || "-"}</Text>
  const environment = pipeline?.environment ? (
    <Badge color={getEnvironmentColor(pipeline.environment)}>{pipeline.environment}</Badge>
  ) : (
    "-"
  )
  const tags = pipeline?.tags ? (
    <TagGroup>
      {pipeline.tags.map((tag) => (
        <Tag size="sm">{tag}</Tag>
      ))}
    </TagGroup>
  ) : (
    "-"
  )

  const actions = (
    <Button icon="play-line" size="sm" variant="text" onClick={() => onSelect(pipeline.pipeline)}>
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

interface PipelinesTableProps {
  pipelines: Pipeline[]
  onSelect: (pipeline: string) => void
}

export default function PipelinesTable({ pipelines, onSelect }: PipelinesTableProps) {
  const headers = TABLE_CONFIG.map((col) => col.header)
  const data = pipelines
    .map((pipeline) => buildTableComponents(pipeline, onSelect))
    .map((comp) => TABLE_CONFIG.map((col) => comp[col.component]))
  return <Table className="fr-pt-0" headers={headers} data={data} />
}
