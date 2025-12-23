import {
  Header as HeaderWrapper,
  Logo,
  Service,
  FastAccess,
  Button,
  Nav,
  Link,
  NavItem,
  // NavItem,
} from "@dataesr/dsfr-plus"
import SwitchTheme from "./switch-theme"
import { useState } from "react"
import { useLocation } from "react-router-dom"

export default function Header() {
  const [isThemeModalOpen, setIsThemeModalOpen] = useState(false)
  const { pathname } = useLocation()

  const openThemeModal = () => {
    setIsThemeModalOpen(true)
  }

  const closeThemeModal = () => {
    setIsThemeModalOpen(false)
  }

  return (
    <HeaderWrapper>
      <Logo splitCharacter="|" text="Ministère|de l'enseignement|supérieur|et de la recherche" />
      <Service name="ML-HUB" tagline="DataESR ML & AI playground" />
      <FastAccess>
        <Button>
          <button
            className="fr-footer__bottom-link fr-icon-theme-fill fr-btn--icon-left"
            aria-controls="fr-theme-modal"
            data-fr-opened={isThemeModalOpen}
            onClick={openThemeModal}
          >
            Paramètres d'affichage
          </button>
        </Button>
      </FastAccess>
      <Nav>
        <Link href="/" current={pathname === "/"}>
          Home
        </Link>
        <Link href="/run" current={pathname.split("/").includes("run")}>
          Run
        </Link>
        <NavItem title="Explore" current={pathname.split("/").includes("explore")}>
          <Link href="/explore?t=models">Models</Link>
          <Link href="/explore?t=datasets">Datasets</Link>
          <Link href="/explore?t=configs">Configs</Link>
        </NavItem>
        <Link href="https://mlflow.staging.dataesr.ovh" target="_blank" rel="noopener noreferrer">
          Track
        </Link>
        <SwitchTheme isOpen={isThemeModalOpen} onClose={closeThemeModal} />
      </Nav>
    </HeaderWrapper>
  )
}
