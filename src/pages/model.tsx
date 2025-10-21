import { useParams } from "react-router-dom"
import { Container, Title, Text, Button, Tag, TagGroup, ButtonGroup } from "@dataesr/dsfr-plus"
import { useHuggingFaceModels } from "../hooks/useHuggingFaceModels"

export default function Model() {
  const { modelId } = useParams<{ modelId: string }>()
  const { data: models, isFetching, error } = useHuggingFaceModels()

  console.log("isFetching", isFetching)
  console.log("error", error)

  if (isFetching || error) return null

  const currentModel = models?.find((model) => model.id === modelId)
  console.log("modelId", modelId)
  console.log("currentModel", currentModel)

  const handleTrain = () => null
  const handleEvaluate = () => null
  const handleInference = () => null

  return (
    <Container className="fr-my-5w">
      <Title as="h3" className="fr-mb-2w">
        {currentModel.name}
      </Title>
      <Text size="md" className="fr-mb-3w">
        {currentModel.config?.model_type && (
          <span className="fr-mr-2w">
            <strong>Type:</strong> {currentModel.config.model_type}
          </span>
        )}
        {currentModel.task && (
          <span className="fr-mr-2w">
            <strong>Task:</strong> {currentModel.task}
          </span>
        )}
        {currentModel.downloads && (
          <span className="fr-mr-2w">
            <strong>Downloads:</strong> {currentModel.downloads.toLocaleString()}
          </span>
        )}
      </Text>
      {currentModel.config?.architectures && currentModel.config.architectures.length > 0 && (
        <div className="fr-mb-3w">
          <Text size="sm" bold className="fr-mb-1w">
            Architectures:
          </Text>
          <TagGroup>
            {currentModel.config.architectures.map((arch, index) => (
              <Tag key={index} color="green-emeraude">
                {arch}
              </Tag>
            ))}
          </TagGroup>
        </div>
      )}
      {currentModel.tags && currentModel.tags.length > 0 && (
        <div className="fr-mb-3w">
          <Text size="sm" bold className="fr-mb-1w">
            Tags:
          </Text>
          <TagGroup>
            {currentModel.tags.map((tag, index) => (
              <Tag key={index} color="blue-cumulus">
                {tag}
              </Tag>
            ))}
          </TagGroup>
        </div>
      )}

      <div className="fr-mb-4w">
        <Text size="sm" bold className="fr-mb-1w">
          Actions:
        </Text>
        <ButtonGroup isInlineFrom="sm">
          <Button onClick={handleTrain}>Train</Button>
          <Button onClick={handleEvaluate}>Evaluate</Button>
          <Button onClick={handleInference}>Inference</Button>
        </ButtonGroup>
        <Button
          icon="external-link-line"
          iconPosition="right"
          variant="secondary"
          onClick={() => window.open(`https://huggingface.co/${currentModel.name}`, "_blank")}
        >
          Voir sur Hugging Face
        </Button>
      </div>
    </Container>
  )
}
