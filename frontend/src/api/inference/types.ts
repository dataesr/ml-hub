import { EnvironmentVariable } from "../../types"

export type InferenceAppState =
  | "QUEUED"
  | "PENDING"
  | "INITIALIZING"
  | "FINALIZING"
  | "RUNNING"
  | "TIMEOUT"
  | "FAILED"
  | "ERROR"
  | "DONE"
  | "INTERRUPTED"
  | "INTERRUPTING"
  | "SYNC_FAILED"

export type InferenceApp = {
  id: string
  createdAt: Date
  updatedAt?: Date
  spec: {
    name: string
    image: string
    envVars?: Array<EnvironmentVariable>
    labels: {
      ["ovh/id"]: string
      ["ovh/type"]: string
    }
    resources: {
      cpu?: number
      gpu?: number
      gpuModel?: string
    }
  }
  status: {
    state: InferenceAppState
    url: string
  }
}

type InferencePromptsParams = Record<string, any>
type InferenceSamplingParams = Record<string, string | number>

export type InferenceInputs = {
  inference_url?: string
  inference_app_id?: string
  inference_app_start?: boolean
  texts: Array<string>
  prompts_params?: InferencePromptsParams
  sampling_params?: InferenceSamplingParams
}

export type InferenceCompletions = {
  completions: Array<string>
  duration: number
}
