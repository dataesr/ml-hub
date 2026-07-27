export type OVHJobState =
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

export type OVHJob = {
  id: string
  name: string
  task: string
  state: OVHJobState
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
  external_url: string
  resources: {
    cpu?: number
    gpu?: number
    gpuModel?: string
  }
  labels: Record<string, string>
}
