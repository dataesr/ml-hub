import {
  Accordion,
  Badge,
  Breadcrumb,
  Button,
  Col,
  Container,
  Link,
  Row,
  Tag,
  TagGroup,
  Text,
  Title,
} from "@dataesr/dsfr-plus"
import { useListJobs, useGetJob } from "../../api/jobs/hooks"
import JobsTable from "./components/jobs-table"
import ErrorCallOut from "../../components/error-call-out"
import LoadingSpinner from "../../components/loading-spinner"
import { useState } from "react"
import JobForm from "./components/jobs-form"
import OVHJobs from "../ovh/jobs"

function JobsHeader() {
  return (
    <Container fluid className="bg-run fr-pb-4w">
      <Container className="fr-pt-2w">
        <Breadcrumb className="fr-pt-2w fr-mt-0 fr-mb-2w">
          <Link href="/">Home</Link>
          <Link current>Run</Link>
        </Breadcrumb>
        <Text size="lead" className="fr-mb-0">
          Pick a job, review its configuration, and launch it.
        </Text>
      </Container>
    </Container>
  )
}

export default function Jobs() {
  const { data, isFetching, error } = useListJobs()
  const [selectedJob, setSelectedJob] = useState<string | null>(null)
  const { data: job, isFetching: isFetchingJob } = useGetJob(selectedJob)
  const selectedJobSummary = data?.find((item) => item.name === selectedJob)

  return (
    <Container fluid>
      <JobsHeader />
      <Container className="fr-my-3w">
        {error && <ErrorCallOut error={error} />}

        <Row gutters>
          <Col xs={12} lg={selectedJob ? 6 : 12}>
            <div className="run-surface fr-card fr-p-3w fr-mb-2w">
              <div className="run-surface__header fr-mb-2w">
                <div>
                  <Title as="h2" look="h5" className="fr-mb-1v">
                    Available jobs
                  </Title>
                  <Text size="sm" className="fr-mb-0">
                    Select a job to inspect its parameters and open the launch panel.
                  </Text>
                </div>
                {data && <Badge>{`${data.length} jobs`}</Badge>}
              </div>
              {isFetching && !data && <LoadingSpinner position="left" />}
              {data && <JobsTable jobs={data} onSelect={setSelectedJob} />}
            </div>
          </Col>

          {selectedJob && (
            <Col xs={12} lg={6}>
              <div className="run-launch-panel fr-card fr-p-3w">
                <div className="run-launch-panel__header fr-mb-2w">
                  <div>
                    <Title as="h2" look="h5" className="fr-mb-1v">
                      {selectedJob}
                    </Title>
                    <Text size="sm" className="fr-mb-0">
                      {selectedJobSummary?.description || "Review the inputs before starting a new run."}
                    </Text>
                  </div>
                  <Button icon="close-line" iconPosition="right" variant="text" onClick={() => setSelectedJob(null)}>
                    Close
                  </Button>
                </div>

                <div className="run-launch-panel__body">
                  {selectedJobSummary?.tags?.length ? (
                    <TagGroup className="fr-mb-2w">
                      {selectedJobSummary.tags.map((tag) => (
                        <Tag key={tag} size="sm">
                          {tag}
                        </Tag>
                      ))}
                    </TagGroup>
                  ) : null}

                  {isFetchingJob && !job && <LoadingSpinner position="left" />}
                  {job && <JobForm job={job} onClose={() => setSelectedJob(null)} />}
                </div>
              </div>
            </Col>
          )}
        </Row>
        <Accordion title="OVH Jobs" className="fr-mt-3w">
          <OVHJobs />
        </Accordion>
      </Container>
    </Container>
  )
}
