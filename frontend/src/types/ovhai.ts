export type OvhaiJobState =
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

export type OvhAiJob = {
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
    state: OvhaiJobState
    url: string
    duration?: number
    exitCode?: number
    queuedAt?: Date
    startedAt?: Date
    finalizedAt?: Date
  }
}
export type OvhAiJobs = Array<OvhAiJob>
