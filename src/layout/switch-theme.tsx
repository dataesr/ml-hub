export default function SwitchTheme({ isOpen, onClose }) {
  return (
    <>
      <dialog
        id="fr-theme-modal"
        className="fr-modal"
        role="dialog"
        aria-labelledby="fr-theme-modal-title"
        open={isOpen}
      >
        <div className="fr-container fr-container--fluid fr-container-md">
          <div className="fr-grid-row fr-grid-row--center">
            <div className="fr-col-12 fr-col-md-6 fr-col-lg-4">
              <div className="fr-modal__body">
                <div className="fr-modal__header">
                  <button
                    className="fr-btn--close fr-btn"
                    aria-controls="fr-theme-modal"
                    id="button-5622"
                    title="Fermer"
                    onClick={onClose}
                  >
                    Fermer
                  </button>
                </div>
                <div className="fr-modal__content">
                  <h1 id="fr-theme-modal-title" className="fr-modal__title">
                    Paramètres d’affichage
                  </h1>
                  <div id="fr-display" className="fr-display">
                    <fieldset className="fr-fieldset" id="display-fieldset">
                      <legend
                        className="fr-fieldset__legend--regular fr-fieldset__legend"
                        id="display-fieldset-legend"
                      >
                        Choisissez un thème pour personnaliser l’apparence du
                        site.
                      </legend>
                      <div className="fr-fieldset__element">
                        <div className="fr-radio-group fr-radio-rich">
                          <input
                            value="light"
                            type="radio"
                            id="fr-radios-theme-light"
                            name="fr-radios-theme"
                          />
                          <label
                            className="fr-label"
                            htmlFor="fr-radios-theme-light"
                          >
                            Thème clair
                          </label>
                          <div className="fr-radio-rich__img">
                            <svg
                              aria-hidden="true"
                              className="fr-artwork"
                              viewBox="0 0 80 80"
                              width="80px"
                              height="80px"
                            >
                              <use
                                className="fr-artwork-decorative"
                                href="/artwork/pictograms/environment/sun.svg#artwork-decorative"
                              />
                              <use
                                className="fr-artwork-minor"
                                href="/artwork/pictograms/environment/sun.svg#artwork-minor"
                              />
                              <use
                                className="fr-artwork-major"
                                href="/artwork/pictograms/environment/sun.svg#artwork-major"
                              />
                            </svg>
                          </div>
                        </div>
                      </div>
                      <div className="fr-fieldset__element">
                        <div className="fr-radio-group fr-radio-rich">
                          <input
                            value="dark"
                            type="radio"
                            id="fr-radios-theme-dark"
                            name="fr-radios-theme"
                          />
                          <label
                            className="fr-label"
                            htmlFor="fr-radios-theme-dark"
                          >
                            Thème sombre
                          </label>
                          <div className="fr-radio-rich__img">
                            <svg
                              aria-hidden="true"
                              className="fr-artwork"
                              viewBox="0 0 80 80"
                              width="80px"
                              height="80px"
                            >
                              <use
                                className="fr-artwork-decorative"
                                href="/artwork/pictograms/environment/moon.svg#artwork-decorative"
                              />
                              <use
                                className="fr-artwork-minor"
                                href="/artwork/pictograms/environment/moon.svg#artwork-minor"
                              />
                              <use
                                className="fr-artwork-major"
                                href="/artwork/pictograms/environment/moon.svg#artwork-major"
                              />
                            </svg>
                          </div>
                        </div>
                      </div>
                      <div className="fr-fieldset__element">
                        <div className="fr-radio-group fr-radio-rich">
                          <input
                            value="system"
                            type="radio"
                            id="fr-radios-theme-system"
                            name="fr-radios-theme"
                          />
                          <label
                            className="fr-label"
                            htmlFor="fr-radios-theme-system"
                          >
                            Systeme
                            <span className="fr-hint-text">
                              Utilise les paramètres systeme
                            </span>
                          </label>
                          <div className="fr-radio-rich__img">
                            <svg
                              aria-hidden="true"
                              className="fr-artwork"
                              viewBox="0 0 80 80"
                              width="80px"
                              height="80px"
                            >
                              <use
                                className="fr-artwork-decorative"
                                href="/artwork/pictograms/system/system.svg#artwork-decorative"
                              />
                              <use
                                className="fr-artwork-minor"
                                href="/artwork/pictograms/system/system.svg#artwork-minor"
                              />
                              <use
                                className="fr-artwork-major"
                                href="/artwork/pictograms/system/system.svg#artwork-major"
                              />
                            </svg>
                          </div>
                        </div>
                      </div>
                    </fieldset>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </dialog>
    </>
  );
}
