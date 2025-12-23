import { useCallback } from "react"
import { Breadcrumb, Container, Link, Text } from "@dataesr/dsfr-plus"
import Datasets from "../datasets"
import Experiments from "../experiments"
import Models from "../models"
import { useSearchParams } from "react-router-dom"

export default function Explore() {
  const [searchParams, setSearchParams] = useSearchParams()
  const currentTab = searchParams.get("t") || "models"

  const handleTabChange = useCallback(
    (tab: string) => {
      searchParams.set("t", tab)
      setSearchParams(searchParams)
    },
    [searchParams, setSearchParams]
  )

  return (
    <Container fluid>
      <Container fluid className="bg-explore fr-pb-0">
        <Container>
          <Breadcrumb className="fr-pt-2w fr-mt-0 fr-mb-2w">
            <Link href="/">Home</Link>
            <Link current>Explore</Link>
          </Breadcrumb>
          <Text size="lead" className="fr-mb-1w">
            Explore models, datasets and experiments
          </Text>
          <nav className="fr-nav xfr-nav--horizontal fr-mb-3w" aria-label="Menu">
            <ul className="fr-nav__list">
              <li className="fr-nav__item">
                <button
                  aria-current={currentTab === "models"}
                  className="fr-nav__link"
                  onClick={() => handleTabChange("models")}
                >
                  Models
                </button>
              </li>
              <li className="fr-nav__item">
                <button
                  aria-current={currentTab === "datasets"}
                  onClick={() => handleTabChange("datasets")}
                  className="fr-nav__link"
                >
                  Datasets
                </button>
              </li>
            </ul>
          </nav>
        </Container>
      </Container>
      {currentTab === "models" && <Models />}
      {currentTab === "datasets" && <Datasets />}
    </Container>
  )
}
