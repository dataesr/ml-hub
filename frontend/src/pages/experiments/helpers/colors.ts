import { ColorFamily } from "@dataesr/dsfr-plus"
import { WandbRunState } from "../../../types/experiments"

export const getStateColor = (state: WandbRunState): ColorFamily => {
  switch (state) {
    case "finished":
      return "green-emeraude"
    case "running":
    case "pending":
      return "blue-cumulus"
    case "crashed":
    case "failed":
      return "beige-gris-galet"
    case "killed":
      return "orange-terre-battue"
    default:
      return "blue-cumulus"
  }
}
