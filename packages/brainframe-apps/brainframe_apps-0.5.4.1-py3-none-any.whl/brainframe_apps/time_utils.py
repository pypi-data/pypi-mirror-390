#
# Copyright (c) 2021 Dilili Labs, Inc.  All rights reserved. Contains Dilili Labs Proprietary Information. RESTRICTED COMPUTER SOFTWARE.  LIMITED RIGHTS DATA.
#

import logging
from time import time


class Timeout:
    def __init__(self, time_seconds, raise_error=True, print_timeout=False):
        self.start: float = time()
        self.time_seconds: float = time_seconds
        self.raise_error: bool = raise_error
        self.print_timeout: float = print_timeout

    def reset(self):
        self.start = time()

    @property
    def elapsed(self) -> float:
        return time() - self.start

    def __bool__(self) -> bool:
        elapsed = self.elapsed
        still_going = elapsed < self.time_seconds

        if not still_going and self.print_timeout:
            logging.warning(f"Timer timed out! Time: {elapsed}")
        if not still_going and self.raise_error:
            raise TimeoutError(
                f"Timer of {self.time_seconds} seconds timed out at {elapsed} seconds!"
            )
        return still_going
