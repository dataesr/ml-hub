import {
  Header as HeaderWrapper,
  Logo,
  Service,
  FastAccess,
  Button,
  Nav,
  Link,
  NavItem,
} from "@dataesr/dsfr-plus";
import SwitchTheme from "./switch-theme";
import { useState } from "react";

export default function Header() {
  const [isThemeModalOpen, setIsThemeModalOpen] = useState(false);

  const openThemeModal = () => {
    setIsThemeModalOpen(true);
  };

  const closeThemeModal = () => {
    setIsThemeModalOpen(false);
  };

  return (
    <HeaderWrapper>
      <Logo
        splitCharacter="|"
        text="Ministère|de l'enseignement|supérieur|et de la recherche"
      />
      <Service name="DOADIFY" tagline="Nouvelle application en developpement" />
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
        <Link href="/">Accueil</Link>
        <Link href="/">DoadiHome</Link>
        <Link href="/">DoadiTest</Link>
        <Link href="/">DoadiNav</Link>
        <Link href="/">DoadiItem</Link>
        <NavItem title={"DoadiNavItem"}>
          <Link href="/">DoadiNavItem</Link>
        </NavItem>
        <SwitchTheme isOpen={isThemeModalOpen} onClose={closeThemeModal} />
      </Nav>
    </HeaderWrapper>
  );
}
