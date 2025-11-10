"""Pipeline infrastructure for OmniGen.

Each pipeline is a self-contained data generation workflow.
Pipelines are registered here and can be loaded dynamically.
"""

from typing import Dict, Type, List
from abc import ABC, abstractmethod


class BasePipeline(ABC):
    """Base class for all pipelines."""
    
    @abstractmethod
    def run(self, config: Dict) -> None:
        """Run the pipeline with given configuration."""
        pass
    
    @classmethod
    @abstractmethod
    def get_name(cls) -> str:
        """Get pipeline name."""
        pass
    
    @classmethod
    @abstractmethod
    def get_description(cls) -> str:
        """Get pipeline description."""
        pass


class PipelineRegistry:
    """Registry for all available pipelines."""
    
    _pipelines: Dict[str, Type[BasePipeline]] = {}
    
    @classmethod
    def register(cls, pipeline_class: Type[BasePipeline]) -> None:
        """Register a pipeline."""
        name = pipeline_class.get_name()
        cls._pipelines[name] = pipeline_class
    
    @classmethod
    def get(cls, name: str) -> Type[BasePipeline]:
        """Get a pipeline by name."""
        if name not in cls._pipelines:
            raise ValueError(
                f"Pipeline '{name}' not found. Available: {', '.join(cls.list())}"
            )
        return cls._pipelines[name]
    
    @classmethod
    def list(cls) -> List[str]:
        """List all registered pipeline names."""
        return list(cls._pipelines.keys())
    
    @classmethod
    def get_info(cls) -> Dict[str, str]:
        """Get info about all pipelines."""
        return {
            name: pipeline.get_description()
            for name, pipeline in cls._pipelines.items()
        }


def load_pipeline(name: str, config: Dict) -> BasePipeline:
    """
    Load a pipeline by name.
    
    Args:
        name: Pipeline name
        config: Pipeline configuration
        
    Returns:
        Pipeline instance
    """
    pipeline_class = PipelineRegistry.get(name)
    return pipeline_class(config)


__all__ = [
    "BasePipeline",
    "PipelineRegistry", 
    "load_pipeline",
]