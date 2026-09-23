import { useCallback } from "react"
import { Breadcrumb, Container, Link, Text } from "@dataesr/dsfr-plus"
import Jobs from "../jobs"
import Configs from "../configs"
import { useSearchParams } from "react-router-dom"

export default function Explore() {
  const [searchParams, setSearchParams] = useSearchParams()
  const currentTab = searchParams.get("t") || "jobs"

  const handleTabChange = useCallback(
    (tab: string) => {
      searchParams.set("t", tab)
      setSearchParams(searchParams)
    },
    [searchParams, setSearchParams],
  )

  return (
    <Container fluid>
      <Container fluid className="bg-explore fr-pb-0">
        <Container>
          <Breadcrumb className="fr-pt-2w fr-mt-0 fr-mb-2w">
            <Link href="/">Home</Link>
            <Link current>Run</Link>
          </Breadcrumb>
          <Text size="lead" className="fr-mb-1w">
            Select a job or a saved configuration, review its parameters, and launch it
          </Text>
          <nav className="fr-nav xfr-nav--horizontal fr-mb-3w" aria-label="Menu">
            <ul className="fr-nav__list">
              <li className="fr-nav__item">
                <button
                  aria-current={currentTab === "jobs"}
                  className="fr-nav__link"
                  onClick={() => handleTabChange("jobs")}
                >
                  Jobs
                </button>
              </li>
              <li className="fr-nav__item">
                <button
                  aria-current={currentTab === "configs"}
                  onClick={() => handleTabChange("configs")}
                  className="fr-nav__link"
                >
                  Configs
                </button>
              </li>
            </ul>
          </nav>
        </Container>
      </Container>
      {currentTab === "jobs" && <Jobs />}
      {currentTab === "configs" && <Configs />}
    </Container>
  )
}
