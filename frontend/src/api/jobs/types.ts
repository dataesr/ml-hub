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
  name: string
  task: string
  state: JobState
  created_at: Date
  updated_at?: Date
  queued_at?: Date
  started_at?: Date
  stopped_at?: Date
  finalized_at?: Date
  duration?: number
  image: string
  command: string
  url: string
  resources: {
    cpu?: number
    gpu?: number
    gpuModel?: string
  }
  labels: Record<string, string>
}

export type JobInputs = {
  name?: string
  gpu?: number
  experiments_params?: Record<string, any>
}

export type JobTrainInputs = JobInputs & {
  model_name: string
  dataset_name: string
  pipeline?: string
  dataset_config?: string
  dataset_format?: "auto" | "conversational" | "text"
  push_model_dir?: string
  hf_push_repo?: string
  prompts_params?: Record<string, any>
  training_params?: Record<string, any>
}

export type JobInfereInputs = JobInputs & {
  model_name: string
  dataset_name: string
  dataset_split?: string
  dataset_config?: string
  prompts_params?: Record<string, any>
  sampling_params?: Record<string, any>
}
