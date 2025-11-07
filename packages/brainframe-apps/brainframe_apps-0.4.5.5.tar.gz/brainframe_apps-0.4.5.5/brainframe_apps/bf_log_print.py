#
# Copyright (c) 2021 Dilili Labs, Inc.  All rights reserved. Contains Dilili Labs Proprietary Information. RESTRICTED COMPUTER SOFTWARE.  LIMITED RIGHTS DATA.
#
# Use logging_factory and do not call these functions directly. BFLogPrint replaces the
# caller generated from findCaller in python logging module.


class BFLogPrint:
    @staticmethod
    def debug(message):
        print(message)

    @staticmethod
    def error(message):
        print(message)

    @staticmethod
    def warning(message):
        print(message)

    @staticmethod
    def info(message):
        print(message)

    @staticmethod
    def critical(message):
        print(message)
