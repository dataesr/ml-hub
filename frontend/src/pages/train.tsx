import { Button, Container, Title } from "@dataesr/dsfr-plus"
import { Table } from "@codegouvfr/react-dsfr/Table"
import { useListJobs } from "../hooks/ovhai"
import { OvhAiJobs } from "../types/ovhai"
import { buildTableComponents } from "../helpers/jobs"
import { postOvhAiJob } from "../api"
import { useState } from "react"
import { useQueryClient } from "@tanstack/react-query"
import { TrainNewModal } from "../components/job-new"

const TABLE_CONFIG = [
  { header: "Name / ID", component: "name" },
  { header: "Status", component: "status" },
  { header: "Resources", component: "resources" },
  { header: "Started", component: "startedAt" },
  { header: "Duration", component: "duration" },
  { header: "Actions", component: "actions" },
]

function TrainTable({ jobs }: { jobs: OvhAiJobs }) {
  const headers = TABLE_CONFIG.map((col) => col.header)
  const data = jobs.map((job) => buildTableComponents(job)).map((job) => TABLE_CONFIG.map((col) => job[col.component]))
  return <Table headers={headers} data={data} />
}

export default function Train() {
  const { data: jobs, isFetching, error } = useListJobs()
  const [isModalOpen, setIsModalOpen] = useState(false)

  if (isFetching || error) return null
  if (!jobs || jobs.length < 1) return "error"

  return (
    <Container className="fr-my-5w">
      <Title as="h2" className="fr-mb-4w">
        Training Jobs
      </Title>
      <Button onClick={() => setIsModalOpen(true)}>New training</Button>
      <TrainTable jobs={jobs} />
      <TrainNewModal isOpen={isModalOpen} onClose={() => null} />
    </Container>
  )
}
