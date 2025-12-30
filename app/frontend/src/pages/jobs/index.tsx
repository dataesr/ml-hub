import { Button, Container } from "@dataesr/dsfr-plus"
import JobsTable from "./components/jobs-table"
import ErrorCallOut from "../../components/error-call-out"
import LoadingSpinner from "../../components/loading-spinner"
import { useListJobs } from "../../api/jobs/hooks"

export default function Jobs() {
  const { data: jobs, isFetching, error, refetch } = useListJobs()

  console.log("jobs", jobs)
  
  return (
    <Container fluid>
        {error && <ErrorCallOut error={error} />}
        {isFetching && !jobs && <LoadingSpinner position="left" />}
      {jobs && (
        <Container fluid>
          <Button className="fr-mb-2w" size="sm" variant="secondary" icon="refresh-line" onClick={() => refetch()}>Refresh</Button>
          <JobsTable jobs={jobs} />
        </Container>
      )}
    </Container>
  )
}
