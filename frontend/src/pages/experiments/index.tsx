import { Container } from "@dataesr/dsfr-plus"
import { useGetArtifact, useListArtifacts } from "../../hooks/experiments"
import { ArtifactKind } from "../../types/experiments"

export default function Experiments() {
  const { data, isFetching, error } = useListArtifacts("TEST", "model")
  const kind: ArtifactKind = "dataset"
  const { data: artifact } = useGetArtifact<typeof kind>("TEST", "model-dataesr_TEST", kind)
  console.log("data", data)
  console.log("isFetching", isFetching)
  console.log("error", error)
  console.log("artifact", artifact, typeof artifact)
  console.log("artifact_meta", artifact.versions[0].metadata.dataset_name)
  return <Container>in progress</Container>
}
