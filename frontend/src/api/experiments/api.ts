import { api } from "../client"
import { Experiment, ExperimentArtifact, ExperimentArtifactBase, ExperimentArtifactKind, ExperimentRun } from "./types"

const API_EXPERIMENTS_URL = "/experiments"
const API_RUNS_URL = API_EXPERIMENTS_URL + "/runs"
const API_ARTIFACTS_URL = API_EXPERIMENTS_URL + "/artifacts"

function buildExperiment(data: any): Experiment {
  return {
    ...data,
    createdAt: data.createdAt ? new Date(data.createdAt) : undefined,
  }
}

function buildRun(data: any): ExperimentRun {
  return {
    ...data,
    createdAt: data.createdAt ? new Date(data.createdAt) : undefined,
  }
}

function buildArtifact(data: any): ExperimentArtifactBase | ExperimentArtifact<ExperimentArtifactKind> {
  return {
    ...data,
    createdAt: data.createdAt ? new Date(data.createdAt) : undefined,
  }
}

export async function listExperiments(): Promise<Experiment[]> {
  const data = await api.get(API_EXPERIMENTS_URL)
  return Array.isArray(data) ? data.map(buildExperiment) : []
}

export async function listExperimentsRuns(project: string): Promise<ExperimentRun[]> {
  const data = await api.get(`${API_RUNS_URL}/${project}`)
  return Array.isArray(data) ? data.map(buildRun) : []
}

export async function getExperimentsRun(project: string, id: string): Promise<ExperimentRun> {
  const data = await api.get(`${API_RUNS_URL}/${project}/${id}`)
  return buildRun(data)
}

export async function listExperimentsArtifacts<K extends ExperimentArtifactKind>(
  project: string,
  type: K
): Promise<Array<ExperimentArtifact<K>>> {
  const data = await api.get(`${API_ARTIFACTS_URL}/${project}?type=${type}`, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  })
  return (Array.isArray(data) ? data.map(buildArtifact) : []) as Array<ExperimentArtifact<K>>
}

export async function getExperimentArtifact<K extends ExperimentArtifactKind>(
  project: string,
  name: string,
  type: ExperimentArtifactKind
): Promise<ExperimentArtifact<K>> {
  const data = await api.get(`${API_ARTIFACTS_URL}/${project}/${name}?type=${type}`)
  return buildArtifact(data) as ExperimentArtifact<K>
}
