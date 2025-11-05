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
    envVars?: any
    defaultHttpPort?: number
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
  name: string
  model_name: string
  dataset_name: string
  gpu?: number
  dataset_format?: "auto" | "conversational" | "text"
  dataset_volume?: boolean
  mode?: "train" | "push"
  push_model_dir?: string
  hf_hub?: string
  hf_hub_private?: boolean
  wandb_name?: string
  wandb_project?: string
  wandb_disabled?: true
}
