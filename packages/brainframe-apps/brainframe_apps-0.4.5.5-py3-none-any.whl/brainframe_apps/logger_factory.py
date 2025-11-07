#
# Copyright (c) 2021 Dilili Labs, Inc.  All rights reserved. Contains Dilili Labs Proprietary Information. RESTRICTED COMPUTER SOFTWARE.  LIMITED RIGHTS DATA.
#

import logging
import os
import sys
import tempfile
from datetime import datetime
from logging import handlers
from pathlib import Path

from brainframe_apps.bf_log_print import BFLogPrint
from pytz import utc


def utcTime(*args):
    utc_dt = utc.localize(datetime.utcnow())
    return utc_dt.timetuple()


def init_logger(logger, path_logs, logger_name="brainframe-apps", level=logging.DEBUG):
    """
    Method to return a custom logger with the given name and level
    """
    logger.setLevel(level)
    format_string = (
        "{asctime} {levelname:<5.5} {filename: <16.16} {lineno:>4}: {message}"
    )
    log_format = logging.Formatter(format_string, style="{")

    # To be consistent with brainframe server, use UTC time
    logging.Formatter.converter = utcTime

    # Creating and adding the console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)
    # Creating and adding the file handler
    if not os.path.isdir(path_logs):
        sys_temp_dir = tempfile.TemporaryDirectory()
        sys_temp_dir_parent = Path(sys_temp_dir.name).parent
        path_logs = str(sys_temp_dir_parent)

    path_logs = str(Path(path_logs, f"{logger_name}.log"))
    # file_handler = handlers.TimedRotatingFileHandler(filename=path_logs, when="D", backupCount=14, encoding='utf-8')
    file_handler = handlers.RotatingFileHandler(
        filename=path_logs,
        maxBytes=(1024 * 1024 * 10),
        backupCount=50,
        encoding="utf-8",
    )
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)

    return logger


logger_not_initialized = True
g_logger = logging.getLogger("brainframe-apps")
bf_log_print = os.getenv("BF_LOG_PRINT")
bf_log_path = os.getenv("BF_LOG_PATH")


# @todo Add logging level support:
#  https://docs.python.org/3/library/logging.html#levels


def get_logger(path_logs=None):
    global logger_not_initialized

    if path_logs is None:
        if bf_log_path is None or bf_log_path == "":
            path_logs = "/tmp"
        else:
            path_logs = bf_log_path

    if bf_log_print is None or bf_log_print != "TRUE":
        if logger_not_initialized:
            # do we care race condition?
            logger_not_initialized = False
            init_logger(g_logger, path_logs)
        return g_logger
    else:
        return BFLogPrint


log = get_logger()

if __name__ == "__main__":
    logger = get_logger()

    for item in range(10):
        logger.debug(f"{item}")

    home = str(Path.home())
    print(f"home={home}")

    temp_dir = tempfile.TemporaryDirectory()
    temp_dir_parent = Path(temp_dir.name).parent
    print(f"temp_dir={temp_dir_parent}")
