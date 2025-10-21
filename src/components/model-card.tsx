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
        title={model.name}
        horizontal
        start={
          <TagGroup>
            <Tag color="blue-cumulus">{model.config.architectures[0]}</Tag>
            {/* {model?.tags?.map((tag) => (
              <Tag>{tag}</Tag>
            ))} */}
            {model?.task && <Tag color="green-emeraude">{model.task}</Tag>}
          </TagGroup>
        }
        footer={
          <Link icon="arrow-right-line" iconPosition="right" href={`https://huggingface.co/${model.name}`} target="_blank">
            See on HuggingFace
          </Link>
        }
        linkProps={{
          href: `model/${model.id}`,
        }}
      />
    </Container>
  )
}
