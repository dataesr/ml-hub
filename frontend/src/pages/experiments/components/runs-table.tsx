import { Table } from "@codegouvfr/react-dsfr/Table"
import CopyToClipboard from "../../../components/copy-to-clipboard"
import { Button, Tag, Text } from "@dataesr/dsfr-plus"
import { formatDate } from "../../../utils"
import { WandbRun } from "../../../types/experiments"
import { getStateColor } from "../helpers/colors"

const TABLE_CONFIG = [
  { header: "Name / ID", component: "name" },
  { header: "Status", component: "status" },
  // { header: "Resources", component: "resources" },
  { header: "Created", component: "createdAt" },
  // { header: "Duration", component: "duration" },
  { header: "Actions", component: "actions" },
]

const buildTableComponents = (run: WandbRun) => {
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
  const status = <Tag color={getStateColor(run.state)}>{run.state}</Tag>
  const createdAt = run.createdAt ? formatDate(run.createdAt) : "-"

  const actions = (
    <Button icon="external-link-line" size="sm" variant="text" onClick={() => window.open(`${run.url}`, "_blank")}>
      Open
    </Button>
  )

  return {
    name,
    status,
    createdAt,
    actions,
  }
}

export default function RunsTable({ runs }: { runs: WandbRun[] }) {
  const headers = TABLE_CONFIG.map((col) => col.header)
  const data = runs.map((run) => buildTableComponents(run)).map((run) => TABLE_CONFIG.map((col) => run[col.component]))
  return <Table className="fr-pt-0" headers={headers} data={data} />
}
