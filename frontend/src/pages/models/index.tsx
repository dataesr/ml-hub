import { Container, Title } from "@dataesr/dsfr-plus"
import { useListModels } from "../../hooks/models"
import ModelCard from "./components/model-card"
import { dateStringToNumber } from "../../utils"

export default function Models() {
  const { data: models, isFetching, error } = useListModels()

  if (isFetching || error) return null

  console.log("models", models)
  return (
    <Container className="fr-my-5w">
      <Title as="h2" className="fr-mb-4w">
        HuggingFace Models
      </Title>
      {models
        .sort(
          (a, b) => dateStringToNumber(b.last_modified || b.created_at) - dateStringToNumber(a.last_modified || a.created_at)
        )
        .map((model) => (
          <ModelCard key={model.id} model={model} />
        ))}
    </Container>
  )
}
