export type HuggingFaceDataset = {
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

export type HuggingFaceDatasets = Array<HuggingFaceDataset>
