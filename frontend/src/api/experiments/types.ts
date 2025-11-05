export type Experiment = {
  id: string
  name: string
  entityName: string
  createdAt: Date
  isBenchmark: boolean
}

export type ExperimentRunState = "crashed" | "failed" | "finished" | "killed" | "running" | "pending"
export type ExperimentRunBase = {
  id: string
  name: string
  displayName: string
  state: ExperimentRunState
  createdAt: Date
  url: string
}
export type ExperimentRun = ExperimentRunBase & {
  tags: Array<string>
  config: Record<string, any>
  group?: string
  jobType?: string
}

export type ExperimentArtifactKind = "model" | "dataset"
type ArtifactSource = "huggingface" | "ovh"
type MetadataByKind<K extends ExperimentArtifactKind> = Extract<ExperimentArtifactMetadata, { kind: K }>

export type ExperimentArtifactMetadata =
  | {
      kind: "model"
      model_name: string
      model_source: ArtifactSource
      path?: string
      hf_hub?: string
      hf_hash?: string
    }
  | {
      kind: "dataset"
      dataset_name: string
      dataset_source: ArtifactSource
      dataset_len: number
      dataset_features: Record<string, string>
      hf_hub?: string
      hf_hash?: string
      path?: string
    }
export type ExperimentArtifactVersion<K extends ExperimentArtifactKind> = {
  version: string
  name: string
  entity: string
  project: string
  aliases: Array<string>
  created_at: Date
  updated_at: Date
  final: boolean
  metadata: MetadataByKind<K>
}

export type ExperimentArtifactBase = {
  id: string
  name: string
  createdAt: Date
  description: string
  tags: Record<string, any>
  aliases: Record<string, any>
}
export type ExperimentArtifact<K extends ExperimentArtifactKind> = ExperimentArtifactBase & {
  versions: Array<ExperimentArtifactVersion<K>>
}
