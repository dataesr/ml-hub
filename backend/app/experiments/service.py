import wandb
from app.logger import get_logger
from app.experiments.schemas import ARTIFACT_TYPES, RUN_STATES

logger = get_logger(__name__)


wb = wandb.Api(overrides={"entity": "dataesr"})


def list_projects():
    projects = wb.projects()
    projects = [project._attrs for project in projects]
    return projects


def get_project(project: str):
    # VBA: doesnt works i dont know why
    project = wb.project(name=project)
    logger.debug(f"{project =} {project.__dict__}")
    return project._attrs


def list_runs(project: str, state: RUN_STATES = None):
    runs = wb.runs(project)
    runs = [
        {
            "id": run.id,
            "name": run.name,
            "displayName": run.displayName,
            "state": run.state,
            "createdAt": run.createdAt,
            "url": run.url,
        }
        for run in runs
    ]
    if state:
        runs = [run for run in runs if run["state"] == state]
    return runs


def get_run(project: str, id: str):
    run = wb.run(path=f"{project}/{id}")
    return run._attrs


def list_artifacts(project: str, type: ARTIFACT_TYPES = "model"):
    artifacts = wb.artifact_collections(project_name=project, type_name=type)
    artifacts = [artifact._attrs for artifact in artifacts]
    return artifacts


def get_artifact(project: str, name: str, type: ARTIFACT_TYPES = "model"):
    artifact_name = f"{project}/{name}"
    artifact = wb.artifact_collection(name=artifact_name, type_name=type)
    artifact = artifact._attrs
    versions = wb.artifacts(name=artifact_name, type_name=type)
    artifact["versions"] = [
        {
            "version": version.version,
            "name": version.name,
            "entity": version.entity,
            "project": version.project,
            "aliases": version.aliases,
            "created_at": version.created_at,
            "final": version._final,
            "metadata": version.metadata,
        }
        for version in versions
    ]
    return artifact
