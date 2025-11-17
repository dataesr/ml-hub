import { Breadcrumb, Button, ButtonGroup, Container, Link, Text } from "@dataesr/dsfr-plus"
import JobsTable from "./components/jobs-table"
import { useNavigate } from "react-router-dom"
import ErrorCallOut from "../../components/error-call-out"
import LoadingSpinner from "../../components/loading-spinner"
import { useListJobs } from "../../api/jobs/hooks"

export default function Jobs() {
  const { data: jobs, isFetching, error, refetch } = useListJobs()
  const navigate = useNavigate()

  return (
    <Container fluid>
      <Container fluid className="bg-train fr-pb-0">
        <Container>
          <Breadcrumb className="fr-pt-2w fr-mt-0 fr-mb-2w">
            <Link href="/">Home</Link>
            <Link current>Train</Link>
          </Breadcrumb>
          <Text size="lead" className="fr-mb-1w">
            Training jobs
          </Text>
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
        </Container>
      </Container>
      <Container className="fr-my-2w">
        {error && <ErrorCallOut error={error} />}
        {isFetching && !jobs && <LoadingSpinner position="left" />}
        {jobs && <JobsTable jobs={jobs} />}
      </Container>
    </Container>
  )
}
