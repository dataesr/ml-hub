import { Badge, Button, Col, Container, Row, Text, Title } from "@dataesr/dsfr-plus"

export default function Home() {
  return (
    <Container fluid className="fr-pb-8w">
      <Container className="fr-pt-6w fr-pb-6w">
        <Row gutters>
          <Col xs={12} lg={7}>
            <div className="home-hero">
              <Badge className="fr-mb-2w">AI Hub</Badge>
              <Title as="h1" className="fr-mb-2w">
                Launch, track, and explore AI workflows.
              </Title>
              <Text className="fr-mb-3w" size="lead">
                A single interface for curated jobs, reproducible runs, and the AI model and dataset catalog.
              </Text>
              <div className="home-hero__actions">
                <Button icon="play-line" as="a" href="/run" style={{ borderRadius: "1rem" }}>
                  Launch a job
                </Button>
                <Button as="a" href="/explore?t=models">
                  Explore assets
                </Button>
              </div>
            </div>
          </Col>
          <Col xs={12} lg={5}>
            <div className="home-highlight fr-p-4w">
              <Text bold className="fr-mb-1w">
                Suggested flow
              </Text>
              <Title as="h2" look="h4" className="fr-mb-2w">
                From config to tracked run
              </Title>
              <div className="home-highlight__step">
                <span>1</span>
                <Text size="sm">Select a ready-to-run job and review its inputs.</Text>
              </div>
              <div className="home-highlight__step">
                <span>2</span>
                <Text size="sm">Launch with structured parameters and environment context.</Text>
              </div>
              <div className="home-highlight__step">
                <span>3</span>
                <Text size="sm">Open MLflow to compare outputs and diagnose regressions.</Text>
              </div>
            </div>
          </Col>
        </Row>
      </Container>
    </Container>
  )
}
