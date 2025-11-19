import { EnvironmentVariable } from "../../types"

export type JobState =
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

export type Job = {
  id: string
  createdAt: Date
  updatedAt?: Date
  spec: {
    name: string
    image: string
    command: Array<string>
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
    state: JobState
    url: string
    duration?: number
    exitCode?: number
    queuedAt?: Date
    startedAt?: Date
    finalizedAt?: Date
  }
}

export type JobInputs = {
  name?: string
  model_name: string
  dataset_name: string
  gpu?: number
  pipeline?: string
  dataset_config?: string
  dataset_format?: "auto" | "conversational" | "text"
  dataset_instruction?: string
  dataset_text_format?: string
  dataset_volume?: boolean
  mode?: "train" | "push"
  push_model_dir?: string
  hf_hub?: string
  hf_hub_private?: boolean
  wandb_project?: string
  wandb_run_tag?: string
  wandb_disabled?: true
}
