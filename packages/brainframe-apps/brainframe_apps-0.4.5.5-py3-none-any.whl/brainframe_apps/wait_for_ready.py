#
# Copyright (c) 2021 Dilili Labs, Inc.  All rights reserved. Contains Dilili Labs Proprietary Information. RESTRICTED COMPUTER SOFTWARE.  LIMITED RIGHTS DATA.
#
from time import time
from typing import Callable

from brainframe.api import bf_errors
from brainframe_apps.logger_factory import log


def wait_for_capsule(fn: Callable, capsule_name, timeout: float = None):
    """A helpful function to automatically wait for a capsule to load if BrainFrame hasn't loaded it yet."""
    start_time = time()
    log.debug(f"    Waiting for {fn.__qualname__}: {capsule_name} to ... ...")
    while timeout is None or time() - start_time < timeout:
        try:
            fn()
            log.debug(f"    Done.")
            break
        except (
            bf_errors.CapsuleNotFoundError,
            bf_errors.InvalidCapsuleOptionError,
            bf_errors.ServerNotReadyError,
        ) as e:
            log.error(f"{e}")
            break
        except Exception as e:
            log.error(f"Exception: {e}")
            break
