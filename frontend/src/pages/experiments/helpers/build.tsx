import { ArtifactKind, WandbArtifact, WandbArtifactBase, WandbProject } from "../../../types/experiments"

export function buildProject(data: any): WandbProject {
  return {
    ...data,
    createdAt: data.createdAt ? new Date(data.createdAt) : undefined,
  }
}

export function buildArtifact(data: any): WandbArtifactBase | WandbArtifact<ArtifactKind> {
  return {
    ...data,
    createdAt: data.createdAt ? new Date(data.createdAt) : undefined,
  }
}
