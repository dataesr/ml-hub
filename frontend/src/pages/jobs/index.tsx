import { Button, Container, Title } from "@dataesr/dsfr-plus"
import { useListJobs } from "../../hooks/jobs"
import JobsTable from "./components/jobs-table"
import { useNavigate } from "react-router-dom"
import ErrorCallOut from "../../components/error-call-out"
import LoadingSpinner from "../../components/loading-spinner"

export default function Jobs() {
  const { data: jobs, isFetching, error } = useListJobs()
  const navigate = useNavigate()

  return (
    <Container className="fr-my-5w">
      <Title as="h2" className="fr-mb-4w">
        Training Jobs
      </Title>
      <Button
        icon="arrow-right-line"
        iconPosition="right"
        onClick={() => navigate("/jobs/submit")}
        disabled={isFetching || error != undefined}
      >
        Submit a new job
      </Button>
      {error && <ErrorCallOut error={error} />}
      {isFetching && <LoadingSpinner position="left" />}
      {!isFetching && jobs && <JobsTable jobs={jobs} />}
    </Container>
  )
}
