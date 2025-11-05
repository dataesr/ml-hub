import { Button, ButtonGroup, Container, Title } from "@dataesr/dsfr-plus"
import JobsTable from "./components/jobs-table"
import { useNavigate } from "react-router-dom"
import ErrorCallOut from "../../components/error-call-out"
import LoadingSpinner from "../../components/loading-spinner"
import { useListJobs } from "../../api/jobs/hooks"

export default function Jobs() {
  const { data: jobs, isFetching, error, refetch } = useListJobs()
  const navigate = useNavigate()

  return (
    <Container className="fr-my-5w">
      <Title as="h2" className="fr-mb-4w">
        Training Jobs
      </Title>
      <Container fluid>
        <ButtonGroup isInlineFrom="xs">
          <Button icon="refresh-line" variant="tertiary" onClick={() => refetch()}>
            Refresh
          </Button>
          <Button
            icon="arrow-right-line"
            iconPosition="right"
            onClick={() => navigate("/jobs/submit")}
            disabled={error != undefined}
          >
            Submit a new job
          </Button>
        </ButtonGroup>
        {error && <ErrorCallOut error={error} />}
        {isFetching && !jobs && <LoadingSpinner position="left" />}
        {jobs && <JobsTable jobs={jobs} />}
      </Container>
    </Container>
  )
}
