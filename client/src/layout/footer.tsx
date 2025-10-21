import { useState } from "react";
import { Container, Link, Logo } from "@dataesr/dsfr-plus";

import {
  Footer,
  FooterBody,
  FooterBottom,
  FooterTop,
} from "./footer-components/index";
import SwitchTheme from "./switch-theme";

export default function MainFooter() {
  const [isThemeModalOpen, setIsThemeModalOpen] = useState(false);

  const openThemeModal = () => {
    setIsThemeModalOpen(true);
  };

  const closeThemeModal = () => {
    setIsThemeModalOpen(false);
  };

  return (
    <>
      <Footer fluid={true}>
        <FooterTop>
          <Container>DOADIFY</Container>
        </FooterTop>
        <FooterBody>
          <Logo
            splitCharacter="|"
            text="Ministère|de l'enseignement|supérieur|et de la recherche"
          />
          <Link
            className="fr-footer__content-link"
            target="_blank"
            rel="noreferrer noopener external"
            title="[À MODIFIER - Intitulé] - nouvelle fenêtre"
            href="https://legifrance.gouv.fr"
          >
            legifrance.gouv.fr
          </Link>
          <Link
            className="fr-footer__content-link"
            target="_blank"
            rel="noreferrer noopener external"
            title="[À MODIFIER - Intitulé] - nouvelle fenêtre"
            href="https://gouvernement.fr"
          >
            gouvernement.fr
          </Link>
          <Link
            className="fr-footer__content-link"
            target="_blank"
            rel="noreferrer noopener external"
            title="[À MODIFIER - Intitulé] - nouvelle fenêtre"
            href="https://service-public.fr"
          >
            service-public.fr
          </Link>
          <Link
            className="fr-footer__content-link"
            target="_blank"
            rel="noreferrer noopener external"
            title="[À MODIFIER - Intitulé] - nouvelle fenêtre"
            href="https://data.gouv.fr"
          >
            data.gouv.fr
          </Link>
        </FooterBody>
        <FooterBottom>
          <button
            className="fr-footer__bottom-link fr-icon-theme-fill fr-btn--icon-left"
            aria-controls="fr-theme-modal"
            data-fr-opened={isThemeModalOpen}
            onClick={openThemeModal}
          >
            Paramètres d'affichage
          </button>
          <SwitchTheme isOpen={isThemeModalOpen} onClose={closeThemeModal} />
        </FooterBottom>
      </Footer>
    </>
  );
}
