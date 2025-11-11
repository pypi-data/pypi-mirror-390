from pruna_pro.algorithms.base.compatibility import extend_compatibility
from pruna_pro.algorithms.base.tags import extend_pro_tags

extend_pro_tags()
from pruna.algorithms.base.registry import AlgorithmRegistry

from pruna_pro import algorithms

AlgorithmRegistry.discover_algorithms(algorithms)
extend_compatibility(AlgorithmRegistry)  # type: ignore[arg-type]

from importlib_metadata import version
from pruna import SmashConfig
from pruna.telemetry import set_telemetry_metrics

from pruna_pro.engine.pruna_pro_model import PrunaProModel
from pruna_pro.smash import smash

set_telemetry_metrics(
    enabled=True, set_as_default=False
)  # Always have telemetry activated by default for Pro, whatever the default

__version__ = version(__name__)

__all__ = ["PrunaProModel", "smash", "SmashConfig", "__version__", "OptimizationAgent"]
