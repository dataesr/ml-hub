import { Button, Container, Title } from "@dataesr/dsfr-plus"
import { useListJobs } from "../../hooks/jobs"
import { useState } from "react"
import JobsTable from "./components/jobs-table"
import { JobsNew } from "./components/jobs-new"

export default function Jobs() {
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
      <JobsTable jobs={jobs} />
      <JobsNew isOpen={isModalOpen} onClose={() => null} />
    </Container>
  )
}
