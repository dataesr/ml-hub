import { ColorFamily } from "@dataesr/dsfr-plus"
import { JobState } from "../../../api/ovh/types"

export const getStateColor = (state: JobState): ColorFamily => {
  switch (state) {
    case "DONE":
      return "green-emeraude"
    case "RUNNING":
    case "INITIALIZING":
    case "FINALIZING":
    case "PENDING":
      return "blue-cumulus"
    case "FAILED":
    case "ERROR":
    case "SYNC_FAILED":
    case "TIMEOUT":
      return "beige-gris-galet"
    case "INTERRUPTED":
    case "INTERRUPTING":
      return "orange-terre-battue"
    default:
      return "blue-cumulus"
  }
}

export const getTaskColor = (task: string): ColorFamily => {
  switch (task) {
    case "finetuning":
    case "training":
      return "yellow-moutarde"
    case "inference":
      return "blue-cumulus"
    default:
      return "beige-gris-galet"
  }
}
