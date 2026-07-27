import { Button, Container } from "@dataesr/dsfr-plus"
import JobsTable from "./components/jobs-table"
import ErrorCallOut from "../../components/error-call-out"
import LoadingSpinner from "../../components/loading-spinner"
import { useListOVHJobs } from "../../api/ovh/hooks"

export default function OVHJobs() {
  const { data: jobs, isFetching, error, refetch } = useListOVHJobs()

  console.log("jobs", jobs)

  return (
    <Container fluid>
      {error && <ErrorCallOut error={error} />}
      {isFetching && !jobs && <LoadingSpinner position="left" />}
      {jobs && (
        <Container fluid>
          <Button className="fr-mb-2w" size="sm" variant="secondary" icon="refresh-line" onClick={() => refetch()}>
            Refresh
          </Button>
          <JobsTable jobs={jobs} />
        </Container>
      )}
    </Container>
  )
}
