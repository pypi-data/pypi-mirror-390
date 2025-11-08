# Copyright (c) 2025 Lightning AI, Inc.
# Licensed under the Lightning.ai Enterprise Add-on EULA (see LICENSE file).
# Contact: support@lightning.ai for commercial licensing.
"""Abstract base class used to build new loggers."""

import functools
from abc import abstractmethod
from argparse import Namespace
from pathlib import Path
from typing import Any, Callable, Union

from lightning_utilities.core.rank_zero import rank_zero_only
from torch import Tensor
from torch.nn import Module

from pytorch_lightning_enterprise.utils.license_validation import LicenseValidator
from pytorch_lightning_enterprise.utils.logger import _scan_checkpoints
from pytorch_lightning_enterprise.utils.types import ModelCheckpointProtocol


class Logger(LicenseValidator):
    """Base class for experiment loggers."""

    def __init__(self):
        super().__init__()
        self._logged_model_time: dict[str, float] = {}

    @property
    @abstractmethod
    def name(self) -> None | str:
        """Return the experiment name."""

    @property
    @abstractmethod
    def version(self) -> None | int | str:
        """Return the experiment version."""

    @property
    def root_dir(self) -> None | str:
        """Return the root directory where all versions of an experiment get saved, or `None` if the logger does not
        save data locally."""
        return None

    @property
    def log_dir(self) -> None | str:
        """Return directory the current version of the experiment gets saved, or `None` if the logger does not save
        data locally."""
        return None

    @property
    def group_separator(self) -> str:
        """Return the default separator used by the logger to group the data into subfolders."""
        return "/"

    @abstractmethod
    def log_metrics(self, metrics: dict[str, float], step: None | int = None) -> None:
        """Records metrics. This method logs metrics as soon as it received them.

        Args:
            metrics: Dictionary with metric names as keys and measured quantities as values
            step: Step number at which the metrics should be recorded

        """
        pass

    @abstractmethod
    def log_hyperparams(self, params: dict[str, Any] | Namespace, *args: Any, **kwargs: Any) -> None:
        """Record hyperparameters.

        Args:
            params: :class:`~argparse.Namespace` or `Dict` containing the hyperparameters
            args: Optional positional arguments, depends on the specific logger being used
            kwargs: Optional keyword arguments, depends on the specific logger being used

        """

    def _scan_and_log_checkpoints(self, checkpoint_callback: ModelCheckpointProtocol) -> None:
        """Scan for new checkpoints and log them using the logger-specific implementation.

        Args:
            checkpoint_callback: The checkpoint callback instance

        """
        # get checkpoints to be saved with associated score
        checkpoints = _scan_checkpoints(checkpoint_callback, self._logged_model_time)

        # log iteratively all new checkpoints
        for t, p, s, _ in checkpoints:
            metadata = {
                # Ensure .item() is called to store Tensor contents
                "score": s.item() if isinstance(s, Tensor) else s,
                "original_filename": Path(p).name,
                "Checkpoint": {
                    k: getattr(checkpoint_callback, k)
                    for k in [
                        "monitor",
                        "mode",
                        "save_last",
                        "save_top_k",
                        "save_weights_only",
                        "_every_n_train_steps",
                        "_every_n_val_epochs",
                    ]
                    # ensure it does not break if `Checkpoint` args change
                    if hasattr(checkpoint_callback, k)
                },
            }
            aliases = ["latest", "best"] if p == checkpoint_callback.best_model_path else ["latest"]

            self._log_checkpoint_artifact(p, metadata, aliases, checkpoint_callback)

            # remember logged models - timestamp needed in case filename didn't change (lastkckpt or custom name)
            self._logged_model_time[p] = t

    @abstractmethod
    def _log_checkpoint_artifact(
        self,
        checkpoint_path: str,
        metadata: dict[str, Any],
        aliases: list[str],
        checkpoint_callback: ModelCheckpointProtocol,
    ) -> None:
        """Log the checkpoint artifact using the logger-specific API.

        This method must be implemented by each logger subclass to handle
        the actual artifact logging in their respective format.

        Args:
            checkpoint_path: Path to the checkpoint file
            metadata: Metadata dictionary for the checkpoint
            aliases: List of aliases for the checkpoint
            checkpoint_callback: The checkpoint callback instance

        """
        pass

    @abstractmethod
    def log_graph(self, model: Module, input_array: None | Tensor = None) -> None:
        """Record model graph.

        Args:
            model: the model with an implementation of ``forward``.
            input_array: input passes to `model.forward`

        """
        pass

    @abstractmethod
    def save(self) -> None:
        """Save log data."""
        pass

    @abstractmethod
    def finalize(self, status: str) -> None:
        """Do any processing that is necessary to finalize an experiment.

        Args:
            status: Status that the experiment finished with (e.g. success, failed, aborted)

        """
        self.save()


class _DummyExperiment:
    """Dummy experiment."""

    def nop(self, *args: Any, **kw: Any) -> None:
        pass

    def __getattr__(self, _: Any) -> Callable:
        return self.nop

    def __getitem__(self, idx: int) -> "_DummyExperiment":
        # enables self.logger.experiment[0].add_image(...)
        return self

    def __setitem__(self, *args: Any, **kwargs: Any) -> None:
        pass


def rank_zero_experiment(fn: Callable) -> Callable:
    """Returns the real experiment on rank 0 and otherwise the _DummyExperiment."""

    @functools.wraps(fn)
    def experiment(self: Any) -> Union[Any, "_DummyExperiment"]:
        """
        Note:
            ``self`` is a custom logger instance. The loggers typically wrap an ``experiment`` method
            with a ``@rank_zero_experiment`` decorator.

            ``Union[Any, _DummyExperiment]`` is used because the wrapped hooks have several return
            types that are specific to the custom logger. The return type here can be considered as
            ``Union[return type of logger.experiment, _DummyExperiment]``.
        """
        if rank_zero_only.rank > 0:
            return _DummyExperiment()
        return fn(self)

    return experiment
