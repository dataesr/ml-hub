import { Container } from "@dataesr/dsfr-plus"
import { useHuggingFaceModels } from "../hooks/useHuggingFaceModels"
import ModelCard from "../components/model-card"

export default function Home() {
  const { data: models, isFetching, error } = useHuggingFaceModels()

  if (isFetching || error) return null

  console.log("models", models)
  return (
    <Container className="fr-my-5w">
      {models
        .sort((a, b) => b.updatedAt.getTime() - a.updatedAt.getTime())
        .map((model) => (
          <ModelCard model={model} />
        ))}
    </Container>
  )
}
