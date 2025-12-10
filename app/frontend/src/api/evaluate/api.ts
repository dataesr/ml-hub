import { api } from "../client"
import { EvaluateTask } from "./types"

const API_EVALUATE_URL = "/evaluate"

function buildEval(data: any): EvaluateTask {
  return {
    ...data,
    queued_at: data.queued_at ? new Date(data.queued_at) : undefined,
    running_at: data.running_at ? new Date(data.running_at) : undefined,
    done_at: data.done_at ? new Date(data.done_at) : undefined,
  }
}

export async function listEvals(): Promise<EvaluateTask[]> {
  const data = await api.get(API_EVALUATE_URL)
  return Array.isArray(data) ? data.map(buildEval) : []
}
