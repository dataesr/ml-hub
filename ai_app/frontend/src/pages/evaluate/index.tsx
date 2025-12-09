import { Breadcrumb, Button, ButtonGroup, Container, Link, Text } from "@dataesr/dsfr-plus"
import { useNavigate } from "react-router-dom"
import ErrorCallOut from "../../components/error-call-out"
import LoadingSpinner from "../../components/loading-spinner"
import { useListEvals } from "../../api/evaluate/hooks"
import EvaluateTable from "./components/evals-table"

export default function Evaluate() {
  const { data: evals, isFetching, error } = useListEvals()
  const navigate = useNavigate()

  return (
    <Container fluid>
      <Container fluid className="bg-evaluate fr-pb-0">
        <Container>
          <Breadcrumb className="fr-pt-2w fr-mt-0 fr-mb-2w">
            <Link href="/">Home</Link>
            <Link current>Evaluate</Link>
          </Breadcrumb>
          <Text size="lead" className="fr-mb-1w">
            Evaluate and compare models
          </Text>
          <ButtonGroup isInlineFrom="xs">
            <Button icon="refresh-line" variant="tertiary" onClick={() => null}>
              Refresh
            </Button>
            <Button
              icon="arrow-right-line"
              iconPosition="right"
              onClick={() => navigate("/evaluate/submit")}
              disabled={false}
            >
              Submit a new evaluation
            </Button>
          </ButtonGroup>
        </Container>
      </Container>
      <Container className="fr-my-2w">
        {error && <ErrorCallOut error={error} />}
        {isFetching && !evals && <LoadingSpinner position="left" />}
        {evals && <EvaluateTable evals={evals} />}
      </Container>
    </Container>
  )
}
