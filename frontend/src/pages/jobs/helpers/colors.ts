import { ColorFamily } from "@dataesr/dsfr-plus"
import { OvhaiJobState } from "../../../types/jobs"

export const getStateColor = (state: OvhaiJobState): ColorFamily => {
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
