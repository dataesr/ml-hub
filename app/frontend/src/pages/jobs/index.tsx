import { Breadcrumb, Container, Link, Text } from "@dataesr/dsfr-plus"
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
        {jobs && <JobsTable jobs={jobs} />}
    </Container>
  )
}
