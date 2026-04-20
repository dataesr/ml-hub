import { Accordion, Breadcrumb, Container, Link, Text } from "@dataesr/dsfr-plus"
import { useListPipelines, useGetPipeline } from "../../api/pipelines/hooks"
import PipelinesTable from "./components/pipelines-table"
import ErrorCallOut from "../../components/error-call-out"
import LoadingSpinner from "../../components/loading-spinner"
import Drawer from "../../components/drawer"
import { useState } from "react"
import PipelineForm from "./components/pipelines-form"
import Jobs from "../jobs"

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
  const { data, isFetching, error } = useListPipelines()
  const [selectedPipeline, setSelectedPipeline] = useState<string | null>(null)
  const { data: pipeline } = useGetPipeline(selectedPipeline)

  return (
    <Container fluid>
      <PipelinesHeader />
      <Container className="fr-my-2w">
        {/* <SearchBar className="fr-mb-2w" style={{ maxWidth: "500px" }} onSearch={() => null} placeholder="Search pipelines..." /> */}
        {selectedPipeline && pipeline && (
          <Drawer anchor="right" isOpen={!!selectedPipeline} onClose={() => setSelectedPipeline(null)}>
            <PipelineForm pipeline={pipeline} />
          </Drawer>
        )}
        {error && <ErrorCallOut error={error} />}
        {isFetching && !data && <LoadingSpinner position="left" />}
        {data && <PipelinesTable pipelines={data} onSelect={setSelectedPipeline} />}
        <Accordion title="Cloud Jobs">
          <Jobs />
        </Accordion>
      </Container>
    </Container>
  )
}
