import { Breadcrumb, Container, Link, SearchBar, Text } from "@dataesr/dsfr-plus"
import { useListPipelines } from "../../api/pipelines/hooks"
import PipelinesTable from "./components/pipelines-table"
import ErrorCallOut from "../../components/error-call-out"
import LoadingSpinner from "../../components/loading-spinner"
import Drawer from "../../components/drawer"
import { useState } from "react"

function PipelinesHeader() {
  return (
    <Container fluid className="bg-run fr-pb-0">
      <Container>
        <Breadcrumb className="fr-pt-2w fr-mt-0 fr-mb-2w">
          <Link href="/">Home</Link>
          <Link current>Run</Link>
        </Breadcrumb>
        <Text size="lead" className="fr-mb-1w fr-pb-1w">
          Run AI pipelines
        </Text>
      </Container>
    </Container>
  )
}

export default function Pipelines() {
  const [isDrawerOpen, setIsDrawerOpen] = useState(false)
  const { data, isFetching, error } = useListPipelines()

  return (
    <Container fluid>
      <PipelinesHeader />
      <Container className="fr-my-2w">
        <SearchBar className="fr-mb-2w" style={{ maxWidth: "500px" }} onSearch={() => null} placeholder="Search pipelines..." />
        <Drawer anchor="right" isOpen={isDrawerOpen} onClose={() => setIsDrawerOpen(false)}>
          <Text>CONTENT...</Text>
        </Drawer>
        {error && <ErrorCallOut error={error} />}
        {isFetching && !data && <LoadingSpinner position="left" />}
        {data && <PipelinesTable pipelines={data} />}
      </Container>
    </Container>
  )
}
