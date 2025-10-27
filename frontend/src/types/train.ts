export type TrainNewJobArgs = {
  name: string
  model_name: string
  dataset_name: string
  gpu?: number
  dataset_format?: "auto" | "conversational" | "text"
  dataset_volume?: boolean
  mode?: "train" | "push"
  push_model_dir?: string
  hf_hub?: string
  hf_hub_private?: boolean
  envs?: Array<{ name: string; value: string }>
}
