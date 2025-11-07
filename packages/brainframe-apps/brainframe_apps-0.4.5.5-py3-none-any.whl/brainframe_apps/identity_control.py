#
# Copyright (c) 2021 Dilili Labs, Inc.  All rights reserved. Contains Dilili Labs Proprietary Information. RESTRICTED COMPUTER SOFTWARE.  LIMITED RIGHTS DATA.
#
import os
if __name__ == "__main__":
    os.environ['BF_LOG_PRINT'] = 'TRUE'

import sys
from argparse import ArgumentParser
from pathlib import Path

from brainframe.api import BrainFrameAPI, bf_codecs, bf_errors
from brainframe_apps.command_utils import by_name, command, subcommand_parse_args
from brainframe_apps.logger_factory import log


def add_identity_images(api, identity, img_bgr, class_name):
    img_id = None
    img_needs_review = False
    try:
        img_id = api.new_storage_as_image(img_bgr)
        api.new_identity_image(identity.id, class_name, img_id)

    except bf_errors.ImageAlreadyEncodedError as err:
        log.warning(f"{err}: {class_name} {identity}")
        img_needs_review = True
    except bf_errors.NoDetectionsInImageError as err:
        log.warning(f"{err}: {class_name} {identity}")
        img_needs_review = True
    except bf_errors.TooManyDetectionsInImageError as err:
        log.warning(f"{err}: {class_name} {identity}")
        img_needs_review = True
    except bf_errors.BaseAPIError as err:
        log.error(f"{err}: {class_name} {identity}")
        img_needs_review = True
    except:
        log.error(f"SOMETHING IS WRONG {bf_errors}")
        img_needs_review = True

    if img_needs_review:
        img_id = None

    return img_id


def add_identity_id(api, unique_name, nickname):
    try:
        identity = bf_codecs.Identity(unique_name, nickname, metadata={})
        identity = api.set_identity(identity)
    except bf_errors.DuplicateIdentityNameError as err:
        # This is ok
        identities, _ = api.get_identities(unique_name=unique_name)
        identity = identities[0]
        log.error(f"{err}, use this one instead: {identity}")
    return identity


def add_identity(api, img_bgr, unique_name, nickname, class_name):
    identity = add_identity_id(api, unique_name, nickname)
    img_id = add_identity_images(api, identity, img_bgr, class_name)

    return identity, img_id


def get_identities(api):
    identities, total_count = api.get_identities()
    return identities, total_count


def delete_identity(api, identity):
    try:
        api.delete_identity(identity.id)
    except bf_errors.IdentityNotFoundError as err:
        log.error(f"{identity}: {err}")


def delete_all_identities(api):
    identities, total_count = get_identities(api)
    for identity in identities:
        delete_identity(api, identity)


def _identity_control_parse_args(parser):
    parser.add_argument(
        "--server-url",
        default="http://localhost",
        help="The URL for the BrainFrame server. Default: %(default)s",
    )
    parser.add_argument(
        "--image-path",
        type=Path,
        default=Path("./images"),
        help="PNG image file name to generate identity. Default: %(default)s",
    )
    parser.add_argument(
        "--unique-name",
        default="Anonymous_001",
        help="unique_name of the identity. Default: %(default)s",
    )
    parser.add_argument(
        "--nickname",
        default="First_LastName",
        help="nickname of the identity. Default: %(default)s",
    )
    parser.add_argument(
        "--class-name",
        default="person",
        help="class_name of the identity. Default: %(default)s",
    )
    parser.add_argument(
        "--cmd",
        default="list",
        help="add, list, or delete_all identities. Default: %(default)s",
    )


@command("identity-control")
def identity_control_main(is_command=True):
    parser = ArgumentParser(
        "This tool will list/add/delete identity from BrainFrame server."
    )
    _identity_control_parse_args(parser)
    args = subcommand_parse_args(parser, is_command)

    # Connect to the BrainFrame Server
    server_url = args.server_url
    log.debug(
        f"{os.path.basename(sys.argv[0])} Waiting for BrainFrame server at '{server_url}'"
    )
    api = BrainFrameAPI(server_url)
    api.wait_for_server_initialization()

    if args.cmd == "list":
        identities, total_count = get_identities(api)
        for identity in identities:
            log.debug(f"    {identity}")
    elif args.cmd == "add":
        identity_image_data = open(args.image_path, "rb")
        identity, img_id = add_identity(
            api,
            identity_image_data.read(),
            args.unique_name,
            args.nickname,
            args.class_name,
        )
        if img_id is None:
            log.error(f"Add {identity} failed")
        else:
            log.debug(f"Add {identity}, {img_id} succeeded")

    elif args.cmd == "delete_all":
        delete_all_identities(api)


if __name__ == "__main__":
    by_name["identity-control"](False)


