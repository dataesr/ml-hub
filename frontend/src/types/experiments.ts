export type WandbProject = {
  id: string
  name: string
  entityName: string
  createdAt: Date
  isBenchmark: boolean
}
export type WandbProjects = Array<WandbProject>

export type WandbRunState = "crashed" | "failed" | "finished" | "killed" | "running" | "pending"
export type WandbRun = {
  id: string
  name: string
  displayName: string
  state: WandbRunState
  createdAt: Date
  url: string
}
export type WandbRuns = Array<WandbRun>

export type ArtifactKind = "model" | "dataset"
type ArtifactSource = "huggingface" | "ovh"
type MetadataByKind<K extends ArtifactKind> = Extract<WandbArtifactMetadata, { kind: K }>

export type WandbArtifactMetadata =
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
export type WandbArtifactVersion<K extends ArtifactKind> = {
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

export type WandbArtifactBase = {
  id: string
  name: string
  createdAt: Date
  description: string
  tags: Record<string, any>
  aliases: Record<string, any>
}
export type WandbArtifact<K extends ArtifactKind> = WandbArtifactBase & {
  versions: Array<WandbArtifactVersion<K>>
}
export type WandbArtifacts = Array<WandbArtifact<ArtifactKind>>
