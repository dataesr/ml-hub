import { Breadcrumb, Button, ButtonGroup, Container, Link, Text } from "@dataesr/dsfr-plus"
// import { useNavigate } from "react-router-dom"
import ErrorCallOut from "../../components/error-call-out"
import LoadingSpinner from "../../components/loading-spinner"
import InferenceAppsTable from "./components/apps-table"
import { useListApps } from "../../api/inference/hooks"

export default function InferenceApps() {
  const { data: apps, isFetching, error, refetch } = useListApps()
  // const navigate = useNavigate()

  return (
    <Container fluid>
      <Container fluid className="bg-inference fr-pb-0">
        <Container>
          <Breadcrumb className="fr-pt-2w fr-mt-0 fr-mb-2w">
            <Link href="/">Home</Link>
            <Link current>Inference</Link>
          </Breadcrumb>
          <Text size="lead" className="fr-mb-1w">
            Inference apps
          </Text>
          <ButtonGroup isInlineFrom="xs">
            <Button icon="refresh-line" variant="tertiary" onClick={() => refetch()}>
              Refresh
            </Button>
            <Button icon="arrow-right-line" iconPosition="right" onClick={() => null} disabled={true}>
              Create a new app
            </Button>
          </ButtonGroup>
        </Container>
      </Container>
      <Container className="fr-my-2w">
        {error && <ErrorCallOut error={error} />}
        {isFetching && !apps && <LoadingSpinner position="left" />}
        {apps && <InferenceAppsTable apps={apps} />}
      </Container>
    </Container>
  )
}
