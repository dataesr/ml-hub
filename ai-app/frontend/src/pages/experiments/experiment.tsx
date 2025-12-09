import { useNavigate, useParams } from "react-router-dom"
import { Container, Title, Text, Button, Tag, TagGroup } from "@dataesr/dsfr-plus"
import { useGetExperiment, useListRuns } from "../../api/experiments/hooks"
import RunsTable from "./components/runs-table"

export default function Experiment() {
  const { id } = useParams<{ id: string }>()
  const { data: experiment, isFetching, error } = useGetExperiment(id)
  const { data: experimentRuns } = useListRuns(id)
  const navigate = useNavigate()

  if (isFetching || error) return null
  console.log("experimentsRuns", experimentRuns)

  return (
    <Container className="fr-my-3w">
      <Button size="sm" variant="tertiary" icon="arrow-left-line" onClick={() => navigate("/explore?t=experiments")}>
        Back to experiments
      </Button>
      <Title as="h3" className="fr-mb-2w fr-mt-5w">
        {experiment.name}
      </Title>
      {experiment.tags && Object.keys(experiment.tags).length > 0 && (
        <div className="fr-mb-3w">
          <Text size="sm" bold className="fr-mb-1w">
            Tags:
          </Text>
          <TagGroup>
            {Object.entries(experiment.tags).map(([key, value], index) => (
              <Tag key={index} color="blue-cumulus">
                {`${key}: ${value}`}
              </Tag>
            ))}
          </TagGroup>
        </div>
      )}
      {experimentRuns && (
        <>
          <Text size="sm" bold className="fr-mb-1w">
            Runs:
          </Text>
          <RunsTable runs={experimentRuns} />
        </>
      )}
      <div className="fr-mb-4w">
        <Text size="sm" bold className="fr-mb-1w">
          Actions:
        </Text>
        <Button
          icon="external-link-line"
          iconPosition="right"
          variant="secondary"
          onClick={() => window.open(experiment.external_url, "_blank")}
        >
          Open on MlFlow
        </Button>
      </div>
    </Container>
  )
}
