export type EvaluateTaskStatus = "queued" | "running" | "done" | "error"

export type EvaluateTask = {
  id: string
  status: EvaluateTaskStatus
  queued_at?: Date
  running_at?: Date
  done_at?: Date
  result?: any
  progress?: number
  error?: string
}
