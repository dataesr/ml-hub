import { api } from "../client"
import { Experiment, ExperimentRun, ExperimentRunBase } from "./types"

const API_EXPERIMENTS_URL = "/experiments"
const API_RUNS_URL = API_EXPERIMENTS_URL + "/runs"

function buildExperiment(data: any): Experiment {
  return {
    ...data,
    created_at: data.created_at ? new Date(data.created_at) : undefined,
    updated_at: data.updated_at ? new Date(data.updated_at) : undefined,
  }
}

function buildRun(data: any): ExperimentRun {
  return {
    ...data,
    start_time: data.start_time ? new Date(data.start_time) : undefined,
    end_time: data.end_time ? new Date(data.end_time) : undefined,
  }
}

export async function listExperiments(): Promise<Experiment[]> {
  const data = await api.get(API_EXPERIMENTS_URL)
  return Array.isArray(data) ? data.map(buildExperiment) : []
}

export async function getExperiment(id: string): Promise<Experiment> {
  const data = await api.get(`${API_EXPERIMENTS_URL}/${id}`)
  return buildExperiment(data)
}

export async function listExperimentsRuns(id: string): Promise<ExperimentRunBase[]> {
  const data = await api.get(`${API_EXPERIMENTS_URL}/${id}/runs`)
  return Array.isArray(data) ? data.map(buildRun) : []
}

export async function getExperimentsRun(run_id: string): Promise<ExperimentRun> {
  const data = await api.get(`${API_RUNS_URL}/${run_id}`)
  return buildRun(data)
}