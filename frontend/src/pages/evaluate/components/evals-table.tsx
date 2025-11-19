import { Table } from "@codegouvfr/react-dsfr/Table"
import CopyToClipboard from "../../../components/copy-to-clipboard"
import { Button, Text } from "@dataesr/dsfr-plus"
import { formatDate, formatDuration } from "../../../utils"
import { EvaluateTask } from "../../../api/evaluate/types"

const TABLE_CONFIG = [
  { header: "ID", component: "name" },
  { header: "Status", component: "status" },
  { header: "QueuedAt", component: "queued_at" },
  { header: "RunningAt", component: "running_at" },
  { header: "DoneAt", component: "done_at" },
  { header: "Duration", component: "duration" },
  { header: "Actions", component: "actions" },
]

const buildTableComponents = (task: EvaluateTask) => {
  const name = (
    <CopyToClipboard copyText={task.id}>
      <Text size="sm" bold>
        {task.id}
      </Text>
    </CopyToClipboard>
  )

  const queued_at = task?.queued_at ? formatDate(task.queued_at) : "-"
  const running_at = task?.running_at ? formatDate(task.running_at) : "-"
  const done_at = task?.done_at ? formatDate(task.done_at) : "-"
  const duration =
    task?.running_at && task?.done_at ? formatDuration(task.done_at.getTime() - task.queued_at.getTime()) : "-"

  const actions = (
    <Button icon="external-link-line" size="sm" variant="text" disabled onClick={() => null}>
      Open
    </Button>
  )

  return {
    name,
    queued_at,
    running_at,
    done_at,
    duration,
    actions,
  }
}

export default function EvaluateTable({ evals }: { evals: EvaluateTask[] }) {
  const headers = TABLE_CONFIG.map((col) => col.header)
  const data = evals.map((task) => buildTableComponents(task)).map((task) => TABLE_CONFIG.map((col) => task[col.component]))
  return <Table className="fr-pt-0" headers={headers} data={data} />
}
