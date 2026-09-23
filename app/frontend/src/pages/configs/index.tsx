import { useState } from "react"
import { Badge, Breadcrumb, Button, Col, Container, Link, Row, Text, Title } from "@dataesr/dsfr-plus"
import { useGetConfig, useListConfigs } from "../../api/configs/hooks"
import { useGetJob } from "../../api/jobs/hooks"
import ErrorCallOut from "../../components/error-call-out"
import LoadingSpinner from "../../components/loading-spinner"
import JobForm from "../jobs/components/jobs-form"

function ConfigsHeader() {
  return (
    <Container fluid className="bg-configue fr-pb-4w">
      <Container className="fr-pt-2w">
        <Breadcrumb className="fr-pt-2w fr-mt-0 fr-mb-2w">
          <Link href="/">Home</Link>
          <Link current>Configs</Link>
        </Breadcrumb>
        <Text size="lead" className="fr-mb-0">
          Select a saved job configuration and launch it with its parameters pre-filled.
        </Text>
      </Container>
    </Container>
  )
}

export default function Configs() {
  const { data, isFetching, error } = useListConfigs()
  const [selectedConfig, setSelectedConfig] = useState<string | null>(null)
  const { data: config, isFetching: isFetchingConfig, error: configError } = useGetConfig(selectedConfig)
  const { data: job, isFetching: isFetchingJob, error: jobError } = useGetJob(config?.base || null)
  const configNames = data ? Object.keys(data).sort() : []

  const initialData = config
    ? {
        args: config.args,
        ...(config.tracking?.project_name ? { mlflow: { experiment: config.tracking.project_name } } : {}),
      }
    : undefined

  return (
    <Container fluid>
      {/* <ConfigsHeader /> */}
      <Container className="fr-my-3w">
        {(error || configError || jobError) && <ErrorCallOut error={error || configError || jobError} />}
        <Row gutters>
          <Col xs={12} lg={selectedConfig ? 6 : 12}>
            <div className="run-surface fr-card fr-p-3w">
              <div className="run-surface__header fr-mb-2w">
                <div>
                  <Title as="h2" look="h5" className="fr-mb-1v">
                    Available configs
                  </Title>
                  <Text size="sm" className="fr-mb-0">
                    Choose a saved YAML configuration to inspect and launch.
                  </Text>
                </div>
                {data && <Badge>{`${configNames.length} configs`}</Badge>}
              </div>
              {isFetching && !data && <LoadingSpinner position="left" />}
              {data && (
                <div className="configs-list">
                  {configNames.map((name) => (
                    <div key={name} className="configs-list__item">
                      <Text bold>
                        {name}
                        <Badge className="fr-ml-2w" color="blue-cumulus">{`${data[name].base}`}</Badge>
                      </Text>
                      <Button icon="play-line" size="sm" variant="text" onClick={() => setSelectedConfig(name)}>
                        Run
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </Col>

          {selectedConfig && (
            <Col xs={12} lg={6}>
              <div className="run-launch-panel fr-card fr-p-3w">
                <div className="run-launch-panel__header fr-mb-2w">
                  <div>
                    <Title as="h2" look="h5" className="fr-mb-1v">
                      {selectedConfig}
                    </Title>
                    <Text size="sm" className="fr-mb-0">
                      {config?.base ? `Job: ${config.base}` : "Loading configuration..."}
                    </Text>
                  </div>
                  <Button icon="close-line" iconPosition="right" variant="text" onClick={() => setSelectedConfig(null)}>
                    Close
                  </Button>
                </div>
                <div className="run-launch-panel__body">
                  {(isFetchingConfig || isFetchingJob) && !job && <LoadingSpinner position="left" />}
                  {job && (
                    <JobForm
                      key={selectedConfig}
                      job={job}
                      initialData={initialData}
                      onClose={() => setSelectedConfig(null)}
                    />
                  )}
                </div>
              </div>
            </Col>
          )}
        </Row>
      </Container>
    </Container>
  )
}
