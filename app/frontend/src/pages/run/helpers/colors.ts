import { DSFRColors } from "@dataesr/dsfr-plus";

export function getEnvironmentColor(environment: string): DSFRColors {
  switch (environment) {
    case "cloud":
      return "blue-cumulus"
    case "local":
      return "brown-cafe-creme"
    default:
      return "beige-gris-galet"
  }
}
