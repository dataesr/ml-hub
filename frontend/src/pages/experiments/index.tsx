import { Container, Select, SelectOption } from "@dataesr/dsfr-plus"
import ErrorCallOut from "../../components/error-call-out"
import LoadingSpinner from "../../components/loading-spinner"
import { useState } from "react"
import RunsTable from "./components/runs-table"
import { useListExperiments, useListRuns } from "../../api/experiments/hooks"

interface ExperimentsRunsArgs {
  id: string
}
function ExperimentsRuns({ id }: ExperimentsRunsArgs) {
  const { data: runs, isFetching, error } = useListRuns(id)

  return (
    <Container fluid>
      {error && <ErrorCallOut error={error} />}
      {isFetching && !runs && <LoadingSpinner position="left" />}
      {runs && <RunsTable runs={runs} />}
    </Container>
  )
}

export default function Experiments() {
  const { data: experiments, isFetching, error } = useListExperiments()
  const [selectedExperimentId, setSelectedExperimentId] = useState<string>("")
  //TODO remove plain id

  console.log("experiments", experiments)
  console.log("selectProjectId", selectedExperimentId)

  return (
    <Container className="fr-my-2w">
      {error && <ErrorCallOut error={error} />}
      {isFetching && <LoadingSpinner position="left" />}
      {!isFetching && experiments && (
        <Container fluid style={{ width: "max-content" }}>
          <Select selectedKey={selectedExperimentId} onSelectionChange={(key) => setSelectedExperimentId(String(key))}>
            {experiments.map(({ id, name }) => (
              <SelectOption key={id}>{name}</SelectOption>
            ))}
          </Select>
          {selectedExperimentId && <ExperimentsRuns id={selectedExperimentId} />}
        </Container>
      )}
    </Container>
  )
}
