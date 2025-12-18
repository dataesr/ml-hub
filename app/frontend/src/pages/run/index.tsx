import { Breadcrumb, Container, Link, Text } from "@dataesr/dsfr-plus"
import { useListPipelines } from "../../api/pipelines/hooks"
import PipelinesTable from "./components/pipelines-table"
import ErrorCallOut from "../../components/error-call-out"
import LoadingSpinner from "../../components/loading-spinner"

function PipelinesHeader() {
  return (
    <Container fluid className="bg-run fr-pb-0">
      <Container>
        <Breadcrumb className="fr-pt-2w fr-mt-0 fr-mb-2w">
          <Link href="/">Home</Link>
          <Link current>Run</Link>
        </Breadcrumb>
        <Text size="lead" className="fr-mb-1w">
          Run AI pipelines
        </Text>
      </Container>
    </Container>
  )
}

export default function Pipelines() {
  const { data, isFetching, error } = useListPipelines()

  return (
    <Container fluid>
      <PipelinesHeader />
      <Container className="fr-my-2w">
        {error && <ErrorCallOut error={error} />}
        {isFetching && !data && <LoadingSpinner position="left" />}
        {data && <PipelinesTable pipelines={data} />}
      </Container>
    </Container>
  )
}
