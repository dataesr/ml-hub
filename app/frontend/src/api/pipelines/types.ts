export type Pipeline = {
  id: string
  name: string
  description?: string
  inputs?: Record<string, any>
  args?: Record<string, any>
  // Add other fields as needed based on the Pydantic model dump
}
