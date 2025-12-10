export type Experiment = {
  id: string
  name: string
  created_at: Date
  updated_at: Date
  tags: Record<string, string>
  runs: number
  external_url: string
}

export type ExperimentRunState = "RUNNING" | "SCHEDULED" | "FINISHED" | "FAILED" | "KILLED"
export type ExperimentRunBase = {
  id: string
  name: string
  status: ExperimentRunState
  start_time: Date
  end_time: Date
  tags: Record<string, string>
  external_url: string
}
export type ExperimentRun = ExperimentRunBase & {
  metrics: any
  params: any
}