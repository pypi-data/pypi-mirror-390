# Copyright (c) 2025 Lightning AI, Inc.
# Licensed under the Lightning.ai Enterprise Add-on EULA (see LICENSE file).
# Contact: support@lightning.ai for commercial licensing.

from collections.abc import MutableSequence
from typing import Callable, Optional, Protocol, runtime_checkable

from torch import Tensor
from typing_extensions import overload


@runtime_checkable
class ModelCheckpointProtocol(Protocol):
    """Protocol defining the interface for model checkpoint callbacks.

    This protocol defines the minimum interface required by loggers to interact with checkpoint callbacks without
    depending on the PyTorch Lightning implementation.

    """

    # Checkpoint configuration attributes
    monitor: Optional[str]
    mode: str
    save_last: Optional[bool]
    save_top_k: int
    save_weights_only: bool
    _every_n_train_steps: int

    # Checkpoint state attributes
    best_model_path: str
    best_model_score: Optional[Tensor]
    last_model_path: str
    current_score: Optional[Tensor]
    best_k_models: dict[str, Tensor]


@runtime_checkable
class Steppable(Protocol):
    """To structurally type ``optimizer.step()``"""

    @overload
    def step(self, closure: None = ...) -> None: ...

    @overload
    def step(self, closure: Callable[[], float]) -> float: ...

    def step(self, closure: Optional[Callable[[], float]] = ...) -> Optional[float]: ...


def _check_data_type(device_ids: object) -> None:
    """Checks that the device_ids argument is one of the following: int, string, or sequence of integers.

    Args:
        device_ids: gpus/tpu_cores parameter as passed to the Trainer

    Raises:
        TypeError:
            If ``device_ids`` of GPU/TPUs aren't ``int``, ``str`` or sequence of ``int```

    """
    msg = "Device IDs (GPU/TPU) must be an int, a string, a sequence of ints, but you passed"
    if device_ids is None:
        raise TypeError(f"{msg} None")
    if isinstance(device_ids, (MutableSequence, tuple)):
        for id_ in device_ids:
            id_type = type(id_)  # because `isinstance(False, int)` -> True
            if id_type is not int:
                raise TypeError(f"{msg} a sequence of {type(id_).__name__}.")
    elif type(device_ids) not in (int, str):
        raise TypeError(f"{msg} {device_ids!r}.")
