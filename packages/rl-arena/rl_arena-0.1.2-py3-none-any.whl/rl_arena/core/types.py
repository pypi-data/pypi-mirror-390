"""Type definitions for RL Arena."""

from typing import Union, Dict, Any
import numpy as np
import numpy.typing as npt

# Type aliases for clarity and flexibility
ObservationType = Union[npt.NDArray[Any], Dict[str, Any], int, float]
ActionType = Union[int, npt.NDArray[Any], Dict[str, Any]]
RewardType = Union[int, float]
InfoType = Dict[str, Any]

# Configuration type
ConfigType = Dict[str, Any]
