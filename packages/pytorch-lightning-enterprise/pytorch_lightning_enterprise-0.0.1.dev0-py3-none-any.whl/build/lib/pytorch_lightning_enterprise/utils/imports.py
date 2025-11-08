# Copyright (c) 2025 Lightning AI, Inc.
# Licensed under the Lightning.ai Enterprise Add-on EULA (see LICENSE file).
# Contact: support@lightning.ai for commercial licensing.

from lightning_utilities.core.imports import RequirementCache

_NUMPY_AVAILABLE = RequirementCache("numpy")

_WANDB_AVAILABLE = RequirementCache("wandb>=0.12.10")
_COMET_AVAILABLE = RequirementCache("comet-ml>=3.44.4")
_MLFLOW_AVAILABLE = RequirementCache("mlflow>=1.0.0")
_MLFLOW_SYNCHRONOUS_AVAILABLE = RequirementCache("mlflow>=2.8.0")
_NEPTUNE_AVAILABLE = RequirementCache("neptune>=1.0")

_BITSANDBYTES_AVAILABLE = RequirementCache("bitsandbytes")
_TRANSFORMER_ENGINE_AVAILABLE = RequirementCache("transformer_engine>=0.11.0")
_DEEPSPEED_AVAILABLE = RequirementCache("deepspeed")

# PJRT support requires this minimum version
_XLA_AVAILABLE = RequirementCache("torch_xla>=1.13", "torch_xla")
_XLA_GREATER_EQUAL_2_1 = RequirementCache("torch_xla>=2.1")
_XLA_GREATER_EQUAL_2_5 = RequirementCache("torch_xla>=2.5")
