import { Breadcrumb, Container, Link, Text } from "@dataesr/dsfr-plus"

export default function Analyze() {
  return (
    <Container fluid>
      <Container fluid className="bg-run fr-pb-0">
        <Container>
          <Breadcrumb className="fr-pt-2w fr-mt-0 fr-mb-2w">
            <Link href="/">Home</Link>
            <Link current>Analyze</Link>
          </Breadcrumb>
          <Text size="lead" className="fr-mb-1w">
            Analyze AI experiments
          </Text>
        </Container>
      </Container>
      <Container>
        <Text>TODO</Text>
      </Container>
    </Container>
  )
}
