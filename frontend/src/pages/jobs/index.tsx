import { Button, Container, Title } from "@dataesr/dsfr-plus"
import { useListJobs } from "../../hooks/jobs"
import JobsTable from "./components/jobs-table"
import { useNavigate } from "react-router-dom"

export default function Jobs() {
  const { data: jobs, isFetching, error } = useListJobs()
  const navigate = useNavigate()

  if (isFetching || error) return null
  if (!jobs || jobs.length < 1) return "error"

  return (
    <Container className="fr-my-5w">
      <Title as="h2" className="fr-mb-4w">
        Training Jobs
      </Title>
      <Button onClick={() => navigate("/jobs/submit")}>Submit a new job</Button>
      <JobsTable jobs={jobs} />
    </Container>
  )
}
