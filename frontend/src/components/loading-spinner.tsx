import { Container, Spinner } from "@dataesr/dsfr-plus"

interface LoadingSpinnerArgs {
  position?: "left" | "center" | "right" | undefined
}
export default function LoadingSpinner({ position }: LoadingSpinnerArgs) {
  return (
    <Container
      className="fr-mt-5w"
      style={{ display: "flex", alignItems: position || "center", justifyContent: position || "center" }}
    >
      <Spinner />
    </Container>
  )
}
