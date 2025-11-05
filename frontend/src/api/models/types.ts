export type Model = {
  _id: string
  id: string
  modelId: string
  author: string
  downloads: number
  config: { architectures: Array<string>; model_type: string }
  created_at: string
  last_modified: string
  pipeline_tag: string
  private: boolean
  tags: Array<string>
}
