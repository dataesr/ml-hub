import { Breadcrumb, Container, Link, SearchBar, Text } from "@dataesr/dsfr-plus"
import { useListPipelines } from "../../api/pipelines/hooks"
import PipelinesTable from "./components/pipelines-table"
import ErrorCallOut from "../../components/error-call-out"
import LoadingSpinner from "../../components/loading-spinner"
import Drawer from "../../components/drawer"
import { useState } from "react"
import { Pipeline } from "../../api/pipelines/types"
import PipelineForm from "./components/pipelines-form"

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
  const [selectedPipeline, setSelectedPipeline] = useState<Pipeline | null>(null)
  const { data, isFetching, error } = useListPipelines()


  return (
    <Container fluid>
      <PipelinesHeader />
      <Container className="fr-my-2w">
        <SearchBar className="fr-mb-2w" style={{ maxWidth: "500px" }} onSearch={() => null} placeholder="Search pipelines..." />
        {selectedPipeline && <Drawer anchor="right" isOpen={!!selectedPipeline} onClose={() => setSelectedPipeline(null)}>
          <PipelineForm pipeline={selectedPipeline} />
        </Drawer>}
        {error && <ErrorCallOut error={error} />}
        {isFetching && !data && <LoadingSpinner position="left" />}
        {data && <PipelinesTable pipelines={data} onSelect={setSelectedPipeline} />}
      </Container>
    </Container>
  )
}
