export type JobConfig = {
  base: string
  args?: Record<string, any>
  tracking?: Record<string, any>
  [key: string]: any
}

export type Configs = Record<string, JobConfig>