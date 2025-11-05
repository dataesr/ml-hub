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
            <Link href={`/datasets/${dataset.id}`}>
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
              icon="external-link-line"
              variant="text"
              onClick={() => window.open(`${HUGGING_FACE_URL}/${dataset.id}`, "_blank")}
            >
              Open
            </Button>
          </Col>
        </Row>
      </Container>
    </Container>
  )
}
