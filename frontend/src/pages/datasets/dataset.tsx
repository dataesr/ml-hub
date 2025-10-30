import { useParams } from "react-router-dom"
import { Container, Title, Text, Button, Tag, TagGroup, ButtonGroup } from "@dataesr/dsfr-plus"
import { HUGGING_FACE_URL } from "../../api"
import { useGetDataset } from "../../hooks/datasets"

export default function Dataset() {
  const { owner, name } = useParams<{ owner: string; name: string }>()
  const { data: currentModel, isFetching, error } = useGetDataset(`${owner}/${name}`)

  if (isFetching || error) return null

  const handleTrain = () => null

  return (
    <Container className="fr-my-5w">
      <Title as="h3" className="fr-mb-2w">
        {currentModel.id}
      </Title>
      <Text size="md" className="fr-mb-3w">
        {currentModel.config?.model_type && (
          <span className="fr-mr-2w">
            <strong>Type:</strong> {currentModel.config.model_type}
          </span>
        )}
        {currentModel.downloads != undefined && (
          <span className="fr-mr-2w">
            <strong>Downloads:</strong> {currentModel.downloads}
          </span>
        )}
      </Text>
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
