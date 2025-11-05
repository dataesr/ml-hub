export type Dataset = {
  _id: string
  id: string
  author: string
  sha: string
  downloads: number
  created_at: string
  last_modified: string
  private: boolean
  tags: Array<string>
}

export type DatasetConfig = {
  name: string
  dataset_name?: string
  instruction?: string
  dataset_format?: "text" | "conversational"
  text_format?: string
  chat_template?: string
}
