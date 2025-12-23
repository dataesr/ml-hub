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
      <Container fluid className="bg-train fr-pb-0">
        <Container>
          <Breadcrumb className="fr-pt-2w fr-mt-0 fr-mb-2w">
            <Link href="/">Home</Link>
            <Link current>Jobs</Link>
          </Breadcrumb>
          <Text size="lead" className="fr-mb-1w">
            OVH Jobs
          </Text>

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
