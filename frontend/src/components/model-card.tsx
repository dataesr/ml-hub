import { Container, Link, Tag, TagGroup } from "@dataesr/dsfr-plus"
import { HuggingFaceModel } from "../types/huggingface"
import { Card } from "@codegouvfr/react-dsfr/Card"

type ModelCardProps = {
  model: HuggingFaceModel
}

export default function ModelCard({ model }: ModelCardProps) {
  return (
    <Container className="fr-card fr-mb-2w">
      <Card
        title={model.id}
        horizontal
        start={
          <TagGroup>
            <Tag color="blue-cumulus">{model.config.architectures[0]}</Tag>
            {/* {model?.tags?.map((tag) => (
              <Tag>{tag}</Tag>
            ))} */}
            {model?.pipeline_tag && <Tag color="green-emeraude">{model.pipeline_tag}</Tag>}
          </TagGroup>
        }
        footer={
          <Link icon="arrow-right-line" iconPosition="right" href={`https://huggingface.co/${model.id}`} target="_blank">
            See on HuggingFace
          </Link>
        }
        linkProps={{
          href: `/model/${model.id}`,
        }}
      />
    </Container>
  )
}
