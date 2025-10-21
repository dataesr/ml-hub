import { Container } from "@dataesr/dsfr-plus";
import SwaggerUI from "swagger-ui-react";
import "swagger-ui-react/swagger-ui.css";

export default function Swagger() {
  return (
    <Container>
      <SwaggerUI url="/api/docs/specs.json" />
    </Container>
  );
}
