"""
MLflow config and lightweight run context manager.
"""

import os
from typing import Any, Optional
import mlflow
from pydantic import BaseModel, Field
from datasets import Dataset
from mlflow.data.dataset_source_registry import resolve_dataset_source
from mlflow.data.meta_dataset import MetaDataset
from core.common.datasets import get_commit_hash
from core.common.ovh import DATASETS_CONTAINER
from core.utils.distributed import is_main_process
from core.utils.logger import get_logger
from core.utils.secrets import SECRET_ENV_MLFLOW
from core.utils.types import ENV

logger = get_logger(__name__)


def mlflow_get_client() -> mlflow.MlflowClient:
    mlflow_uri = os.getenv("MLFLOW_TRACKING_URI")
    if not mlflow_uri:
        raise ValueError("MLFLOW_TRACKING_URI not set, disable Mlflow monitoring.")

    client = mlflow.MlflowClient(tracking_uri=mlflow_uri)
    return client


class MLflowConfig(BaseModel):
    tracking_uri: Optional[str] = None  # falls back to $MLFLOW_TRACKING_URI when None
    experiment: str = "Default"
    run_name: str = "run"
    run_name_tag: Optional[str] = None

    def get_envs(self) -> list[ENV]:
        """Return environment variables needed to propagate this config to a remote job."""
        envs: list[ENV] = []
        if self.experiment:
            envs.append(ENV(name="MLFLOW_EXPERIMENT_NAME", value=self.experiment))
        if self.run_name:
            envs.append(ENV(name="MLFLOW_RUN_NAME", value=self.run_name))
        if self.run_name_tag:
            envs.append(ENV(name="MLFLOW_RUN_NAME_TAG", value=self.run_name_tag))
        envs.extend(SECRET_ENV_MLFLOW)
        return envs


class MLflowRun:
    """
    Lightweight MLflow context manager.

    Starts a run on entry and ends it on exit.  All calls are no-ops when
    running on a non-rank-0 process or when no tracking URI is available.
    """

    cfg: MLflowConfig = Field(default_factory=MLflowConfig)
    enabled: bool = False
    _run_started: bool = False

    def __init__(self, cfg: Optional[MLflowConfig] = None, enabled: Optional[bool] = None):
        self._run_started = False
        if cfg is not None:
            self.cfg = cfg
            self.enabled = is_main_process() if enabled is None else enabled

    def __enter__(self) -> "MLflowRun":
        if not self.enabled:
            return self

        tracking_uri = self.cfg.tracking_uri or os.environ.get("MLFLOW_TRACKING_URI")
        if not tracking_uri:
            logger.warning("MLflow tracking URI not set — disabling MLflow logging")
            self.enabled = False
            return self

        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(self.cfg.experiment)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if not self.enabled or not self._run_started:
            return
        if exc_type is not None:
            mlflow.set_tag("status", "failed")
        mlflow.end_run()

    def start_run(self, run_name: Optional[str] = None, tags: Optional[dict[str, str]] = None) -> None:
        if self.enabled:
            name = run_name or self.cfg.run_name
            mlflow.start_run(run_name=to_alpha_num(name), tags=tags)
            self._run_started = True

    def log_params(self, params: dict[str, Any]) -> None:
        if self.enabled:
            mlflow.log_params(params)

    def log_metrics(self, metrics: dict[str, Any], step: int | None = None) -> None:
        if self.enabled:
            mlflow.log_metrics(metrics, step=step)

    def log_artifact(self, path: str, artifact_path: str = ""):
        if self.enabled and os.path.exists(path):
            mlflow.log_artifact(str(path), artifact_path=artifact_path)

    def log_artifacts(self, path: str, artifact_path: str = "") -> None:
        if self.enabled and os.path.exists(path):
            mlflow.log_artifacts(str(path), artifact_path=artifact_path)

    def log_dict(self, data: dict, artifact_file: str = ""):
        if self.enabled:
            mlflow.log_dict(data, artifact_file)

    def log_dataset(self, dataset_name: str, dataset: Dataset, dataset_split: str | None = None, **metadata):
        if not self.enabled:
            return

        name = to_alpha_num(dataset_name)
        commit_hash = get_commit_hash(dataset)
        if commit_hash:
            metadata["commit_hash"] = commit_hash
            raw_source = dataset
        else:
            raw_source = f"s3://{os.path.join(DATASETS_CONTAINER, dataset_name)}"

        try:
            dataset_source = resolve_dataset_source(raw_source)
            mlflow_dataset = MetaDataset(source=dataset_source, name=name)
            mlflow.log_input(mlflow_dataset, context=dataset_split, tags=metadata)
            logger.debug(f"Logged dataset {dataset_name} metadata")
        except Exception as error:
            logger.warning(f"Error while logging dataset {dataset_name}: {error}")

    def log_model(self, model_name: str, model, tokenizer):
        if not self.enabled:
            return

        register_name = os.getenv("MLFLOW_MODEL_NAME") or os.getenv("HF_PUSH_REPO") or model_name
        model_info = mlflow.transformers.log_model(
            transformers_model={"model": model, "tokenizer": tokenizer},
            tokenizer=tokenizer,
            name=to_alpha_num(register_name, replace_dots=True),
            registered_model_name=to_alpha_num(register_name),
        )
        logger.debug(f"Logged model {model_info.registered_model_version} (id={model_info.model_id})")
        mlflow.set_tags({"model_version": model_info.registered_model_version, "model_id": model_info.model_id})

    def set_active_model(self, model_name: str | None = None, model_id: str | None = None):
        if not self.enabled:
            return

        model_id = model_id or os.getenv("MLFLOW_ACTIVE_MODEL_ID")
        model_name = model_name or os.getenv("MLFLOW_MODEL_NAME")
        if not model_id or not model_name:
            logger.warning("No model_id and model_name found, traces won't be linked to a model!")
            return

        mlflow.set_active_model(model_id=model_id, name=model_name)
        logger.debug(f"Active model {model_id or model_name} has been set for tracking.")


def to_alpha_num(name: str, replace_dots: bool = False) -> str:
    """Make sure the name fits alpha num naming rules (A-Za-z0-9_.-)"""
    last_name = name.split("/")[-1]
    clean_name = last_name.replace(" ", "-").replace(":", "-")
    if replace_dots:
        clean_name = clean_name.replace(".", "-")
    return clean_name.lower()
