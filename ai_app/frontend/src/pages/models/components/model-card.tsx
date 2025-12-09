import { Button, Col, Container, Link, Row, Tag, TagGroup } from "@dataesr/dsfr-plus"
import { HUGGING_FACE_URL } from "../../../api/url"
import { Model } from "../../../api/models/types"

const filterTags = (tag: string) => !["region"].some((filter) => tag.includes(filter))

interface ModelCardProps {
  model: Model
}
export default function ModelCard({ model }: ModelCardProps) {
  return (
    <Container className="fr-card fr-mb-1w">
      <Container className="fr-mt-2w">
        <Row>
          <Col xs="10">
            <Link href={`/models/${model.id}`}>
              <strong>{model.id}</strong>
            </Link>
            <TagGroup className="fr-mt-2w">
              <Tag size="sm" color="blue-cumulus">
                {model.config.architectures[0]}
              </Tag>
              {model?.tags?.filter(filterTags).map((tag) => (
                <Tag size="sm">{tag}</Tag>
              ))}
              {model?.pipeline_tag && (
                <Tag size="sm" color="green-emeraude">
                  {model.pipeline_tag}
                </Tag>
              )}
            </TagGroup>
          </Col>
          <Col xs="2">
            <Button
              icon="external-link-line"
              variant="text"
              onClick={() => window.open(`${HUGGING_FACE_URL}/${model.id}`, "_blank")}
            >
              Open
            </Button>
          </Col>
        </Row>
      </Container>
    </Container>
  )
}
