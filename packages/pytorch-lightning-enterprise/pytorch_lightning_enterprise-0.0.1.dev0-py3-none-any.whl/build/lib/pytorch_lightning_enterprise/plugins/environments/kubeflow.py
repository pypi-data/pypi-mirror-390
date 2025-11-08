# Copyright (c) 2025 Lightning AI, Inc.
# Licensed under the Lightning.ai Enterprise Add-on EULA (see LICENSE file).
# Contact: support@lightning.ai for commercial licensing.

import logging
import os

from pytorch_lightning_enterprise.utils.license_validation import LicenseValidator

log = logging.getLogger(__name__)


class KubeflowEnvironment(LicenseValidator):
    """Environment for distributed training using the `PyTorchJob`_ operator from `Kubeflow`_.

    This environment, unlike others, does not get auto-detected and needs to be passed to the Fabric/Trainer
    constructor manually.

    .. _PyTorchJob: https://www.kubeflow.org/docs/components/trainer/legacy-v1/user-guides/pytorch/
    .. _Kubeflow: https://www.kubeflow.org

    """

    @property
    def creates_processes_externally(self) -> bool:
        return True

    @property
    def main_address(self) -> str:
        return os.environ["MASTER_ADDR"]

    @property
    def main_port(self) -> int:
        return int(os.environ["MASTER_PORT"])

    @staticmethod
    def detect() -> bool:
        raise NotImplementedError("The Kubeflow environment can't be detected automatically.")

    def world_size(self) -> int:
        return int(os.environ["WORLD_SIZE"])

    def set_world_size(self, size: int) -> None:
        log.debug("KubeflowEnvironment.set_world_size was called, but setting world size is not allowed. Ignored.")

    def global_rank(self) -> int:
        return int(os.environ["RANK"])

    def set_global_rank(self, rank: int) -> None:
        log.debug("KubeflowEnvironment.set_global_rank was called, but setting global rank is not allowed. Ignored.")

    def local_rank(self) -> int:
        return 0

    def node_rank(self) -> int:
        return self.global_rank()
