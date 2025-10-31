import { ArtifactKind, WandbArtifact, WandbArtifactBase, WandbProject, WandbRun } from "../../../types/experiments"

export function buildProject(data: any): WandbProject {
  return {
    ...data,
    createdAt: data.createdAt ? new Date(data.createdAt) : undefined,
  }
}

export function buildRun(data: any): WandbRun {
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
