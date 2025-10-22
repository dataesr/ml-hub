import { Container } from "@dataesr/dsfr-plus"
import { useListModels } from "../hooks/huggingface"
import ModelCard from "../components/model-card"

export default function Home() {
  const { data: models, isFetching, error } = useListModels()

  if (isFetching || error) return null

  console.log("models", models)
  return (
    <Container className="fr-my-5w">
      {models
        .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
        .map((model) => (
          <ModelCard key={model.id} model={model} />
        ))}
    </Container>
  )
}
