import { Container, Title, Button, Tag, ColorFamily, Text } from "@dataesr/dsfr-plus"
import { Table } from "@codegouvfr/react-dsfr/Table"
import { useListJobs } from "../hooks/ovhai"
import { OvhAiJob, OvhAiJobs, OvhaiJobState } from "../types/ovhai"
import { buildTableComponents } from "../helpers/job"

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

const tableConfig = [
  { header: "Name / ID", component: "name" },
  { header: "Status", component: "status" },
  { header: "Resources", component: "resources" },
  { header: "Started", component: "startedAt" },
  { header: "Duration", component: "duration" },
  { header: "Actions", component: "actions" },
]

function TrainTable({ jobs }: { jobs: OvhAiJobs }) {
  const headers = tableConfig.map((col) => col.header)
  const data = jobs.map((job) => buildTableComponents(job)).map((job) => tableConfig.map((col) => job[col.component]))

  return <Table headers={headers} data={data} />
}

export default function Train() {
  const { data: jobs, isFetching, error } = useListJobs()

  if (isFetching || error) return null
  if (!jobs || jobs.length < 1) return "error"

  return (
    <Container className="fr-my-5w">
      <Title as="h2" className="fr-mb-4w">
        Training Jobs
      </Title>
      <TrainTable jobs={jobs} />
    </Container>
  )
}
