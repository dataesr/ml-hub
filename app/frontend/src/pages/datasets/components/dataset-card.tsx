import { Button, Col, Container, Link, Row, Tag, TagGroup } from "@dataesr/dsfr-plus"
import { HUGGING_FACE_URL } from "../../../api/url"
import { Dataset } from "../../../api/datasets/types"

const filterTags = (tag: string) => !["library", "region", "language"].some((filter) => tag.includes(filter))

interface DatasetCardProps {
  dataset: Dataset
}
export default function DatasetCard({ dataset }: DatasetCardProps) {
  return (
    <Container className="fr-card fr-mb-1w">
      <Container className="fr-mt-2w">
        <Row>
          <Col xs="10">
            <Link href={`${HUGGING_FACE_URL}/datasets/${dataset.id}`} target="_blank" rel="noopener noreferrer">
              <strong>{dataset.id}</strong>
            </Link>
            <TagGroup className="fr-mt-2w">
              {dataset?.tags?.filter(filterTags).map((tag) => (
                <Tag size="sm">{tag}</Tag>
              ))}
            </TagGroup>
          </Col>
          <Col xs="2">
            <Button
              icon="more-line"
              variant="text"
              disabled
              onClick={() => null}
            >
              Actions
            </Button>
          </Col>
        </Row>
      </Container>
    </Container>
  )
}
