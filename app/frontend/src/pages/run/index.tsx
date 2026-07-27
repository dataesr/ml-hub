import { Accordion, Breadcrumb, Container, Link, Text } from "@dataesr/dsfr-plus"
import { useListJobs, useGetJob } from "../../api/jobs/hooks"
import JobsTable from "./components/jobs-table"
import ErrorCallOut from "../../components/error-call-out"
import LoadingSpinner from "../../components/loading-spinner"
import Drawer from "../../components/drawer"
import { useState } from "react"
import JobForm from "./components/jobs-form"
import OVHJobs from "../ovh/jobs"

function JobsHeader() {
  return (
    <Container fluid className="bg-run fr-pb-0">
      <Container>
        <Breadcrumb className="fr-pt-2w fr-mt-0 fr-mb-2w">
          <Link href="/">Home</Link>
          <Link current>Run</Link>
        </Breadcrumb>
        <Text size="lead" className="fr-mb-1w fr-pb-1w">
          Run AI jobs
        </Text>
      </Container>
    </Container>
  )
}

export default function Jobs() {
  const { data, isFetching, error } = useListJobs()
  const [selectedJob, setSelectedJob] = useState<string | null>(null)
  const { data: job } = useGetJob(selectedJob)

  return (
    <Container fluid>
      <JobsHeader />
      <Container className="fr-my-2w">
        {/* <SearchBar className="fr-mb-2w" style={{ maxWidth: "500px" }} onSearch={() => null} placeholder="Search jobs..." /> */}
        {selectedJob && job && (
          <Drawer anchor="right" isOpen={!!selectedJob} onClose={() => setSelectedJob(null)}>
            <JobForm job={job} />
          </Drawer>
        )}
        {error && <ErrorCallOut error={error} />}
        {isFetching && !data && <LoadingSpinner position="left" />}
        {data && <JobsTable jobs={data} onSelect={setSelectedJob} />}
        <Accordion title="OVH Jobs">
          <OVHJobs />
        </Accordion>
      </Container>
    </Container>
  )
}
