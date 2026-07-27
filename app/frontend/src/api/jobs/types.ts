export type Job = {
  name: string
  description?: string
  tags?: Array<string>
  inputs?: Record<string, any>
  args?: Record<string, any>
  ovh?: Record<string, any>
  mlflow?: Record<string, any>
}
