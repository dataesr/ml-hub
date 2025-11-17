import { Breadcrumb, Container, Link, Text } from "@dataesr/dsfr-plus"

export default function Evaluate() {
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
        </Container>
      </Container>
      <Container className="fr-my-2w">in progress ....</Container>
    </Container>
  )
}
