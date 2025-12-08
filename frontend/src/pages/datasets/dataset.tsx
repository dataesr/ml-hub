import { useNavigate, useParams } from "react-router-dom"
import { Container, Title, Text, Button, Tag, TagGroup, ButtonGroup } from "@dataesr/dsfr-plus"
import { useGetDataset } from "../../api/datasets/hooks"
import { HUGGING_FACE_URL } from "../../api/url"

export default function Dataset() {
  const { owner, name } = useParams<{ owner: string; name: string }>()
  const { data: currentDataset, isFetching, error } = useGetDataset(`${owner}/${name}`)
  const navigate = useNavigate()

  if (isFetching || error) return null

  const handleTrain = () => null

  return (
    <Container className="fr-my-3w">
      <Button size="sm" variant="tertiary" icon="arrow-left-line" onClick={() => navigate("/explore?t=datasets")}>
        Back to datasets
      </Button>
      <Title as="h3" className="fr-mb-2w fr-mt-5w">
        {currentDataset.id}
      </Title>
      <Text size="md" className="fr-mb-3w">
        {currentDataset.downloads != undefined && (
          <span className="fr-mr-2w">
            <strong>Downloads:</strong> {currentDataset.downloads}
          </span>
        )}
      </Text>
      {currentDataset.tags && currentDataset.tags.length > 0 && (
        <div className="fr-mb-3w">
          <Text size="sm" bold className="fr-mb-1w">
            Tags:
          </Text>
          <TagGroup>
            {currentDataset.tags.map((tag, index) => (
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
          onClick={() => window.open(`${HUGGING_FACE_URL}/${currentDataset.id}`, "_blank")}
        >
          Open on HuggingFace
        </Button>
      </div>
    </Container>
  )
}
