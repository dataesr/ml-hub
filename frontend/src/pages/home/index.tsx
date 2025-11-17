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
            desc="Explore DataESR models, datasets and more."
            enlargeLink
            imageAlt="texte alternatif de l’image"
            imageUrl="artwork/pictograms/digital/search.svg"
            classes={{ imgTag: "fr-ratio-1x1" }}
            linkProps={{
              href: "/explore",
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
            desc="Train new models."
            enlargeLink
            imageAlt="texte alternatif de l’image"
            imageUrl="artwork/pictograms/system/system.svg"
            classes={{ imgTag: "fr-ratio-1x1" }}
            linkProps={{
              href: "/jobs",
            }}
            size="small"
            title="Train"
            titleAs="h3"
          />
        </Col>
        <Col xs={12} sm={6} lg={6} xl={3}>
          <Card
            background
            shadow
            desc="Evaluate and compare models."
            enlargeLink
            imageAlt="texte alternatif de l’image"
            imageUrl="artwork/pictograms/digital/data-visualization.svg"
            classes={{ imgTag: "fr-ratio-1x1" }}
            linkProps={{
              href: "/evaluate",
            }}
            size="small"
            title="Evaluate"
            titleAs="h3"
          />
        </Col>
        <Col xs={12} sm={6} lg={6} xl={3}>
          <Card
            background
            shadow
            desc="Infere models."
            enlargeLink
            imageAlt="texte alternatif de l’image"
            imageUrl="artwork/pictograms/leisure/community.svg"
            classes={{ imgTag: "fr-ratio-1x1" }}
            linkProps={{
              href: "/inference",
            }}
            size="small"
            title="Inference"
            titleAs="h3"
          />
        </Col>
      </Row>
    </Container>
  )
}
