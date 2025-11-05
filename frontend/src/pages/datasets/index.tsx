import { Container, Title } from "@dataesr/dsfr-plus"
import { dateStringToNumber } from "../../utils"
import ErrorCallOut from "../../components/error-call-out"
import LoadingSpinner from "../../components/loading-spinner"
import DatasetCard from "./components/dataset-card"
import { Dataset } from "../../api/datasets/types"
import { useListDatasets } from "../../api/datasets/hooks"

function DatasetsList({ datasets }: { datasets: Dataset[] }) {
  const sortedDatasets = datasets.sort(
    (a, b) => dateStringToNumber(b.last_modified || b.created_at) - dateStringToNumber(a.last_modified || a.created_at)
  )

  return (
    <Container fluid style={{ maxWidth: "900px" }}>
      {sortedDatasets.map((dataset) => (
        <DatasetCard key={dataset.id} dataset={dataset} />
      ))}
    </Container>
  )
}

export default function Datasets() {
  const { data: datasets, isFetching, error } = useListDatasets()

  return (
    <Container className="fr-my-5w">
      <Title as="h2" className="fr-mb-4w">
        HuggingFace Datasets
      </Title>
      {error && <ErrorCallOut error={error} />}
      {isFetching && <LoadingSpinner position="left" />}
      {!isFetching && datasets && <DatasetsList datasets={datasets} />}
    </Container>
  )
}
