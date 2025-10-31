import { Container, Select, SelectOption, Title } from "@dataesr/dsfr-plus"
import { useListExperiments, useListRuns } from "../../hooks/experiments"
import ErrorCallOut from "../../components/error-call-out"
import LoadingSpinner from "../../components/loading-spinner"
import { useState } from "react"
import RunsTable from "./components/runs-table"

interface ExperimentsRunsArgs {
  project: string
}
function ExperimentsRuns({ project }: ExperimentsRunsArgs) {
  const { data: runs, isFetching, error } = useListRuns(project)
  console.log("project", project)

  return (
    <Container fluid>
      {error && <ErrorCallOut error={error} />}
      {isFetching && !runs && <LoadingSpinner position="left" />}
      {runs && <RunsTable runs={runs} />}
    </Container>
  )
}

export default function Experiments() {
  const { data: projects, isFetching, error } = useListExperiments()
  const [selectProjectId, setSelectProjectId] = useState<string>(projects?.[0]?.id || "")

  console.log("selectProjectId", selectProjectId)

  return (
    <Container className="fr-my-5w">
      <Title as="h2" className="fr-mb-4w">
        W&B Experiments
      </Title>
      {error && <ErrorCallOut error={error} />}
      {isFetching && <LoadingSpinner position="left" />}
      {!isFetching && projects && (
        <Container fluid style={{ width: "max-content" }}>
          <Select selectedKey={selectProjectId} onSelectionChange={(key) => setSelectProjectId(String(key))}>
            {projects.map(({ id, name }) => (
              <SelectOption key={id}>{name}</SelectOption>
            ))}
          </Select>
          {selectProjectId && <ExperimentsRuns project={projects.find(({ id }) => id == selectProjectId).name} />}
        </Container>
      )}
    </Container>
  )
}
