import { Container } from "@dataesr/dsfr-plus"
import ModelCard from "./components/model-card"
import { dateStringToNumber } from "../../utils"
import ErrorCallOut from "../../components/error-call-out"
import LoadingSpinner from "../../components/loading-spinner"
import { Model } from "../../api/models/types"
import { useListModels } from "../../api/models/hooks"

function ModelsList({ models }: { models: Model[] }) {
  const sortedModels = models.sort(
    (a, b) => dateStringToNumber(b.last_modified || b.created_at) - dateStringToNumber(a.last_modified || a.created_at)
  )

  return (
    <Container fluid style={{ maxWidth: "900px" }}>
      {sortedModels.map((model) => (
        <ModelCard key={model.id} model={model} />
      ))}
    </Container>
  )
}

export default function Models() {
  const { data: models, isFetching, error } = useListModels()

  return (
    <Container className="fr-my-2w">
      {error && <ErrorCallOut error={error} />}
      {isFetching && <LoadingSpinner position="left" />}
      {!isFetching && models && <ModelsList models={models} />}
    </Container>
  )
}
