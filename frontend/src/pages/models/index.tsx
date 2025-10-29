import { Container, Title } from "@dataesr/dsfr-plus"
import { useListModels } from "../../hooks/models"
import ModelCard from "./components/model-card"
import { dateStringToNumber } from "../../utils"
import ErrorCallOut from "../../components/error-call-out"
import { HuggingFaceModels } from "../../types/models"
import LoadingSpinner from "../../components/loading-spinner"

function ModelsList({ models }: { models: HuggingFaceModels }) {
  const sortedModels = models.sort(
    (a, b) => dateStringToNumber(b.last_modified || b.created_at) - dateStringToNumber(a.last_modified || a.created_at)
  )

  return (
    <Container fluid style={{ maxWidth: "1000px" }}>
      {sortedModels.map((model) => (
        <ModelCard key={model.id} model={model} />
      ))}
    </Container>
  )
}

export default function Models() {
  const { data: models, isFetching, error } = useListModels()
  console.log("error", error)

  console.log("models", models)

  return (
    <Container className="fr-my-5w">
      <Title as="h2" className="fr-mb-4w">
        HuggingFace Models
      </Title>
      {error && <ErrorCallOut error={error} />}
      {isFetching && <LoadingSpinner position="left" />}
      {!isFetching && models && <ModelsList models={models} />}
    </Container>
  )
}
