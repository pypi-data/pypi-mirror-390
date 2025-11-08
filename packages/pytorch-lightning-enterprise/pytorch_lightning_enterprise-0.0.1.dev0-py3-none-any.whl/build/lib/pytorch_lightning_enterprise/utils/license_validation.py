# Copyright (c) 2025 Lightning AI, Inc.
# Licensed under the Lightning.ai Enterprise Add-on EULA (see LICENSE file).
# Contact: support@lightning.ai for commercial licensing.

import os
from contextlib import suppress
from functools import lru_cache

from lightning_sdk.api.utils import _get_cloud_url
from lightning_sdk.utils.config import Config, DefaultConfigKeys
from lightning_sdk.utils.license import License
from lightning_utilities.core import WarningCache
from requests import HTTPError

_PYTORCH_LIGHTNING_LICENSE_ENV_VAR = "PYTORCH_LIGHTNING_LICENSE_KEY"
_PYTORCH_LIGHTNING_PRODUCT_NAME = "pytorch-lightning"

warning_cache = WarningCache()


class LicenseValidator:
    def __init__(self):
        try:
            valid_license = validate_license()
            if valid_license:
                return
        except HTTPError:
            warning_cache.warn(license_message_no_internet())

        raise LightningLicenseValidationError(license_message())


@lru_cache(1)
def validate_license() -> bool:
    cfg = Config()

    license_key = os.environ.get(
        _PYTORCH_LIGHTNING_LICENSE_ENV_VAR,
        cfg.get_value(f"{DefaultConfigKeys.license}.{_PYTORCH_LIGHTNING_PRODUCT_NAME}"),
    )
    print(f"{license_key=}")
    if license_key is not None:
        with suppress(Exception):
            valid_license = License(license_key=license_key, product_name=_PYTORCH_LIGHTNING_PRODUCT_NAME).validate()
            print(f"{valid_license=}")
            if valid_license:
                cfg.set(f"{DefaultConfigKeys.license}.{_PYTORCH_LIGHTNING_PRODUCT_NAME}", license_key)
                return True
    return False


def license_message() -> str:
    return (
        f"no valid license found! visit {_get_cloud_url()}/license?product={_PYTORCH_LIGHTNING_PRODUCT_NAME} "
        "for retrieving a license and/or instructions how to use it."
    )


def license_message_no_internet() -> str:
    return (
        "Could not validate license due to internet connection errors. "
        f"Make sure to check license terms at {_get_cloud_url()}/license?product={_PYTORCH_LIGHTNING_PRODUCT_NAME}."
    )


class LightningLicenseValidationError(Exception):
    pass
