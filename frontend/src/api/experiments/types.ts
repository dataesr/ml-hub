export type Experiment = {
  id: string
  name: string
  created_at: Date
  updated_at: Date
  tags: Record<string, string>
}

export type ExperimentRunState = "RUNNING" | "SCHEDULED" | "FINISHED" | "FAILED" | "KILLED"
export type ExperimentRunBase = {
  id: string
  name: string
  displayName: string
  state: ExperimentRunState
  createdAt: Date
  url: string
}
export type ExperimentRun = ExperimentRunBase & {
  tags: Array<string>
  config: Record<string, any>
  group?: string
  jobType?: string
}