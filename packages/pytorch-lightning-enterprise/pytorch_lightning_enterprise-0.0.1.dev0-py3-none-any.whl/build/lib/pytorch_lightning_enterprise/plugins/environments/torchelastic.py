# Copyright (c) 2025 Lightning AI, Inc.
# Licensed under the Lightning.ai Enterprise Add-on EULA (see LICENSE file).
# Contact: support@lightning.ai for commercial licensing.

import logging
import os

import torch.distributed
from lightning_utilities.core.rank_zero import rank_zero_warn

from pytorch_lightning_enterprise.utils.license_validation import LicenseValidator

log = logging.getLogger(__name__)


class TorchElasticEnvironment(LicenseValidator):
    """Environment for fault-tolerant and elastic training with `torchelastic <https://pytorch.org/elastic/>`_"""

    @property
    def creates_processes_externally(self) -> bool:
        return True

    @property
    def main_address(self) -> str:
        if "MASTER_ADDR" not in os.environ:
            rank_zero_warn("MASTER_ADDR environment variable is not defined. Set as localhost")
            os.environ["MASTER_ADDR"] = "127.0.0.1"
        log.debug(f"MASTER_ADDR: {os.environ['MASTER_ADDR']}")
        return os.environ["MASTER_ADDR"]

    @property
    def main_port(self) -> int:
        if "MASTER_PORT" not in os.environ:
            rank_zero_warn("MASTER_PORT environment variable is not defined. Set as 12910")
            os.environ["MASTER_PORT"] = "12910"
        log.debug(f"MASTER_PORT: {os.environ['MASTER_PORT']}")

        return int(os.environ["MASTER_PORT"])

    @staticmethod
    def detect() -> bool:
        """Returns ``True`` if the current process was launched using the torchelastic command."""
        # if not available (for example on MacOS), `is_torchelastic_launched` is not defined
        return torch.distributed.is_available() and torch.distributed.is_torchelastic_launched()

    def world_size(self) -> int:
        return int(os.environ["WORLD_SIZE"])

    def set_world_size(self, size: int) -> None:
        log.debug("TorchElasticEnvironment.set_world_size was called, but setting world size is not allowed. Ignored.")

    def global_rank(self) -> int:
        return int(os.environ["RANK"])

    def set_global_rank(self, rank: int) -> None:
        log.debug(
            "TorchElasticEnvironment.set_global_rank was called, but setting global rank is not allowed. Ignored."
        )

    def local_rank(self) -> int:
        return int(os.environ["LOCAL_RANK"])

    def node_rank(self) -> int:
        return int(os.environ.get("GROUP_RANK", 0))

    def validate_settings(self, num_devices: int, num_nodes: int) -> None:
        if num_devices * num_nodes != self.world_size():
            raise ValueError(
                f"You set `devices={num_devices}` and `num_nodes={num_nodes}` in Lightning, but the product"
                f" ({num_devices} * {num_nodes}) does not match the world size ({self.world_size()})."
            )
