import { Container, Select, SelectOption } from "@dataesr/dsfr-plus"
import ErrorCallOut from "../../components/error-call-out"
import LoadingSpinner from "../../components/loading-spinner"
import { useState } from "react"
import RunsTable from "./components/runs-table"
import { useListExperiments, useListRuns } from "../../api/experiments/hooks"
import { Experiment } from "../../api/experiments/types"
import ExperimentCard from "./components/experiment-card"

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

function ExperimentsList({ experiments }: { experiments: Experiment[] }) {
  const sortedExperiments = experiments.sort(
    (a, b) => (b.updated_at || b.created_at).getTime() - (a.updated_at || a.created_at).getTime()
  )

  return (
    <Container fluid style={{ maxWidth: "900px" }}>
      {sortedExperiments.map((experiment) => (
        <ExperimentCard key={experiment.id} experiment={experiment} />
      ))}
    </Container>
  )
}

export default function Experiments() {
  const { data: experiments, isFetching, error } = useListExperiments()
  // const [selectedExpId, setSelectedExpId] = useState<string>("")
  //TODO remove plain id

  console.log("experiments", experiments)
  // console.log("selectProjectId", selectedExpId)

  return (
    <Container className="fr-my-2w">
      {error && <ErrorCallOut error={error} />}
      {isFetching && <LoadingSpinner position="left" />}
      {!isFetching && experiments && <ExperimentsList experiments={experiments} />}
      {/* {!isFetching && experiments && (
        <Container fluid style={{ width: "max-content" }}>
          <Select selectedKey={selectedExpId} onSelectionChange={(key) => setSelectedExpId(String(key))}>
            {experiments.map(({ id, name }) => (
              <SelectOption key={id}>{name}</SelectOption>
            ))}
          </Select>
          {selectedExpId && <ExperimentsRuns id={selectedExpId} />}
        </Container>
      )} */}
    </Container>
  )
}
