import { Col, Container, Row, Title } from "@dataesr/dsfr-plus"
import { Card } from "@codegouvfr/react-dsfr/Card"

export default function Home() {
  return (
    <Container className="fr-my-5w">
      <Title as="h2" className="fr-mb-10w">
        Home
      </Title>
      <Row gutters>
        <Col xs={12} sm={6} lg={6} xl={3}>
          <Card
            background
            shadow
            desc="Run AI jobs."
            enlargeLink
            imageAlt="system"
            imageUrl="artwork/pictograms/system/system.svg"
            classes={{ imgTag: "fr-ratio-1x1" }}
            linkProps={{
              href: "/run",
            }}
            size="small"
            title="Run"
            titleAs="h3"
          />
        </Col>
        <Col xs={12} sm={6} lg={6} xl={3}>
          <Card
            background
            shadow
            desc="Explore DataESR models, datasets and more."
            enlargeLink
            imageAlt="digital-search"
            imageUrl="artwork/pictograms/digital/search.svg"
            classes={{ imgTag: "fr-ratio-1x1" }}
            linkProps={{
              href: "/explore?t=models",
            }}
            size="small"
            title="Explore"
            titleAs="h3"
          />
        </Col>

        <Col xs={12} sm={6} lg={6} xl={3}>
          <Card
            background
            shadow
            desc="Track and compare your runs."
            enlargeLink
            imageAlt="digital-data-visualization"
            imageUrl="artwork/pictograms/digital/data-visualization.svg"
            classes={{ imgTag: "fr-ratio-1x1" }}
            linkProps={{
              href: "https://mlflow.staging.dataesr.ovh",
              target: "_blank",
              rel: "noopener noreferrer",
            }}
            size="small"
            title="Track"
            titleAs="h3"
          />
        </Col>
        {/* <Col xs={12} sm={6} lg={6} xl={3}>
          <Card
            background
            shadow
            desc="Infere models."
            enlargeLink
            imageAlt="leisure-community"
            imageUrl="artwork/pictograms/leisure/community.svg"
            classes={{ imgTag: "fr-ratio-1x1" }}
            linkProps={{
              href: "/inference",
            }}
            size="small"
            title="Inference"
            titleAs="h3"
          />
        </Col> */}
      </Row>
    </Container>
  )
}
