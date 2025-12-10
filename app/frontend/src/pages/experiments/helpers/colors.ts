import { ColorFamily } from "@dataesr/dsfr-plus"
import { ExperimentRunState } from "../../../api/experiments/types"

export const getStateColor = (state: ExperimentRunState): ColorFamily => {
  switch (state) {
    case "FINISHED":
      return "green-emeraude"
    case "RUNNING":
    case "SCHEDULED":
      return "blue-cumulus"
    case "FAILED":
    case "KILLED":
      return "orange-terre-battue"
    default:
      return "beige-gris-galet"
  }
}

export const getTypeColor = (task: string): ColorFamily => {
  switch (task) {
    case "training":
      return "yellow-moutarde"
    case "inference":
      return "blue-cumulus"
    case "evaluation":
      return "green-emeraude"
    default:
      return "beige-gris-galet"
  }
}
