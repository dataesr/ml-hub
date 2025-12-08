import { Table } from "@codegouvfr/react-dsfr/Table"
import CopyToClipboard from "../../../components/copy-to-clipboard"
import { Badge, Button, Tag, Text } from "@dataesr/dsfr-plus"
import { formatDate, formatDuration } from "../../../utils"
import { getStateColor, getTypeColor } from "../helpers/colors"
import { ExperimentRun } from "../../../api/experiments/types"

const TABLE_CONFIG = [
  { header: "Name / ID", component: "name" },
  { header: "Type", component: "type" },
  { header: "Status", component: "status" },
  { header: "Model", component: "model" },
  { header: "Started", component: "startTime" },
  { header: "Duration", component: "duration" },
  { header: "Actions", component: "actions" },
]

const buildTableComponents = (run: ExperimentRun) => {
  const name = (
    <>
      <CopyToClipboard copyText={run.name}>
        <Text size="sm" bold>
          {run.name}
        </Text>
      </CopyToClipboard>
      <CopyToClipboard copyText={run.id}>
        <Text className="fr-text-mention--grey" size="sm">
          {run.id}
        </Text>
      </CopyToClipboard>
    </>
  )
  const status = <Tag color={getStateColor(run.status)}>{run.status}</Tag>
  const startTime = run.start_time ? formatDate(run.start_time) : "-"
  const duration =
    run.end_time && run.start_time ? formatDuration((run.end_time.getTime() - run.start_time.getTime()) / 1000) : "-"

  const type = run?.tags?.run_type ? <Badge color={getTypeColor(run.tags.run_type)}>{run.tags.run_type}</Badge> : "-"
  const model = run?.tags?.model_name || "-"

  const actions = (
    <Button icon="external-link-line" size="sm" variant="text" onClick={() => window.open(run.external_url, "_blank")}>
      Open
    </Button>
  )

  return {
    name,
    status,
    startTime,
    duration,
    type,
    model,
    actions,
  }
}

export default function RunsTable({ runs }: { runs: ExperimentRun[] }) {
  const headers = TABLE_CONFIG.map((col) => col.header)
  const data = runs.map((run) => buildTableComponents(run)).map((run) => TABLE_CONFIG.map((col) => run[col.component]))
  return <Table className="fr-pt-0" headers={headers} data={data} />
}
