import { useNavigate, useParams } from "react-router-dom"
import { Container, Title, Text, Button, Tag, TagGroup, ButtonGroup } from "@dataesr/dsfr-plus"
import { HUGGING_FACE_URL } from "../../api/url"
import { useGetModel } from "../../api/models/hooks"

export default function Model() {
  const { owner, name } = useParams<{ owner: string; name: string }>()
  const { data: currentModel, isFetching, error } = useGetModel(`${owner}/${name}`)
  const navigate = useNavigate()

  if (isFetching || error) return null

  const handleTrain = () => null
  const handleEvaluate = () => null
  const handleInference = () => null

  return (
    <Container className="fr-my-3w">
      <Button size="sm" variant="tertiary" icon="arrow-left-line" onClick={() => navigate("/explore?t=models")}>
        Back to models
      </Button>
      <Title as="h3" className="fr-mb-2w fr-mt-5w">
        {currentModel.id}
      </Title>
      <Text size="md" className="fr-mb-3w">
        {currentModel.config?.model_type && (
          <span className="fr-mr-2w">
            <strong>Type:</strong> {currentModel.config.model_type}
          </span>
        )}
        {currentModel.pipeline_tag && (
          <span className="fr-mr-2w">
            <strong>Task:</strong> {currentModel.pipeline_tag}
          </span>
        )}
        {currentModel.downloads != undefined && (
          <span className="fr-mr-2w">
            <strong>Downloads:</strong> {currentModel.downloads}
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
          onClick={() => window.open(`${HUGGING_FACE_URL}/${currentModel.id}`, "_blank")}
        >
          Open on HuggingFace
        </Button>
      </div>
    </Container>
  )
}
