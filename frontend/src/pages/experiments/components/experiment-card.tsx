import { Button, Col, Container, Link, Row, Tag, TagGroup } from "@dataesr/dsfr-plus"
import { Experiment } from "../../../api/experiments/types"

const filterTags = (tag: string) => !["mlflow.experimentKind"].some((filter) => tag.includes(filter))

interface ExperimentCardProps {
  experiment: Experiment
}
export default function ExperimentCard({ experiment }: ExperimentCardProps) {
  return (
    <Container className="fr-card fr-mb-1w">
      <Container className="fr-mt-2w">
        <Row>
          <Col xs="10">
            <Link href={`/experiments/${experiment.id}`}>
              <strong>{experiment.name}</strong>
            </Link>
            <TagGroup className="fr-mt-2w">
              {experiment?.tags?.["mlflow.experimentKind"] && (
                <Tag size="sm" color="blue-cumulus">
                  {experiment.tags["mlflow.experimentKind"]}
                </Tag>
              )}

              {Object.keys(experiment?.tags || {})
                ?.filter(filterTags)
                .map((tag) => (
                  <Tag size="sm">{tag}</Tag>
                ))}
            </TagGroup>
          </Col>
          <Col xs="2">
            <Button
              icon="external-link-line"
              variant="text"
              disabled
              onClick={() => window.open(`/${experiment.id}`, "_blank")}
            >
              Open
            </Button>
          </Col>
        </Row>
      </Container>
    </Container>
  )
}
