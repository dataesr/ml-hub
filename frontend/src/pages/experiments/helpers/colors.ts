import { ColorFamily } from "@dataesr/dsfr-plus"
import { ExperimentRunState } from "../../../api/experiments/types"

export const getStateColor = (state: ExperimentRunState): ColorFamily => {
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
