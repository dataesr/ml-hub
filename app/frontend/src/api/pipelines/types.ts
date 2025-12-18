export type Pipeline = {
  pipeline: string
  description?: string
  tags?: Array<string>
  environment?: string
  inputs?: Record<string, any>
  args?: Record<string, any>
  infrastructure?: Record<string, any>
}
