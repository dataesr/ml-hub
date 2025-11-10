import { Button, ButtonGroup, Container, Title } from "@dataesr/dsfr-plus"
// import { useNavigate } from "react-router-dom"
import ErrorCallOut from "../../components/error-call-out"
import LoadingSpinner from "../../components/loading-spinner"
import InferenceAppsTable from "./components/apps-table"
import { useListApps } from "../../api/inference/hooks"

export default function InferenceApps() {
  const { data: apps, isFetching, error, refetch } = useListApps()
  // const navigate = useNavigate()

  return (
    <Container className="fr-my-5w">
      <Title as="h2" className="fr-mb-4w">
        Inference Apps
      </Title>
      <Container fluid>
        <ButtonGroup isInlineFrom="xs">
          <Button icon="refresh-line" variant="tertiary" onClick={() => refetch()}>
            Refresh
          </Button>
          <Button icon="arrow-right-line" iconPosition="right" onClick={() => null} disabled={true}>
            Create a new app
          </Button>
        </ButtonGroup>
        {error && <ErrorCallOut error={error} />}
        {isFetching && !apps && <LoadingSpinner position="left" />}
        {apps && <InferenceAppsTable apps={apps} />}
      </Container>
    </Container>
  )
}
