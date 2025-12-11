from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Any


class PipelineRunnerBase(ABC):
    """
    Abstract Base Class (Interface) for all registered pipelines.
    """

    def __init__(self, config: BaseModel):
        self.config = config

    @abstractmethod
    def run(self) -> Any:
        """
        The main execution method for the pipeline logic.
        """
        raise NotImplementedError("Pipeline class must implement the 'run' method.")
