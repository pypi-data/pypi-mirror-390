#
# Copyright (c) 2023 Dilili Labs, Inc.  All rights reserved. Contains Dilili Labs Proprietary Information. RESTRICTED COMPUTER SOFTWARE.  LIMITED RIGHTS DATA.
#
import os
if __name__ == "__main__":
    os.environ['BF_LOG_PRINT'] = 'TRUE'

from argparse import ArgumentParser

from brainframe.api import BrainFrameAPI, bf_codecs, bf_errors

from .cognito_defs import COGNITO_PORTS
from .cognito_signin import get_cognito_access_token
from .command_utils import by_name, command, subcommand_parse_args
from .domain_defs import BFL_USER, BFL_USER_PASSWORD
from .domain_signin import domain_signin
from .logger_factory import log


def set_cloud_tokens(api, access_token, refresh_token):
    tokens = bf_codecs.CloudTokens(
        access_token=access_token,
        refresh_token=refresh_token,
    )

    try:
        user_info, license_info = api.set_cloud_tokens(tokens)
    except Exception as e:
        user_info, license_info = None, None
        log.debug(f"set_cloud_tokens failed: {e}")

    return user_info, license_info


def get_user_info(api):
    try:
        user_info = api.get_current_cloud_user()
    except Exception as e:
        user_info = None
        message_str = f"get_user_info failed {e}"
        log.error(f"get_user_info failed {e}")

    return user_info


def get_oauth2_info(api):
    try:
        oauth2_info = api.get_oauth2_info()
    except Exception as e:
        oauth2_info = {}
        log.error(f"get_oauth2_info failed {e}")

    return oauth2_info


def _user_control_parse_args(parser):
    parser.add_argument(
        "--server-url",
        default="http://localhost",
        help="The BrainFrame server " "URL, Default: %(default)s",
    )
    parser.add_argument(
        "--bfm-https-cert",
        help="The cert of BrainFrame Management Server, Default: %(default)s",
    )
    parser.add_argument(
        "--access-token",
        default=None,
        help="The OAuth2 JWT access token of an user. Default: %(default)s",
    )
    parser.add_argument(
        "--refresh-token",
        default=None,
        help="The OAuth2 JWT refresh token of an user. Default: %(default)s",
    )
    parser.add_argument(
        "--username",
        default=BFL_USER,
        help="The domain user. Default: %(default)s",
    )
    parser.add_argument(
        "--password",
        default=BFL_USER_PASSWORD,
        help="The password of the domain user. Default: %(default)s",
    )


@command("user-control")
def user_control(is_command=True):
    parser = ArgumentParser(description="User control of a BrainFrame deployment")
    _user_control_parse_args(parser)
    args = subcommand_parse_args(parser, is_command)

    # Connect to BrainFrame server
    api = BrainFrameAPI(args.server_url)

    log.debug(f"{str(parser.prog)} Waiting for server at {args.server_url} ...")

    try:
        api.wait_for_server_initialization(timeout=15)
    except (TimeoutError, bf_errors.ServerNotReadyError):
        log.error(f"BrainFrame server connection timeout")
        return

    if args.access_token is not None and args.refresh_token is not None:
        access_token = args.access_token
        refresh_token = args.refresh_token
    else:
        oauth2_info = get_oauth2_info(api)
        log.info(f"get_oauth2_info: {oauth2_info}")
        if (
            oauth2_info is None
            or not hasattr(oauth2_info, "client_id")
            or not hasattr(oauth2_info, "domain")
            or not hasattr(oauth2_info, "scopes")
        ):
            return {}

        client_id = oauth2_info.client_id
        domain = oauth2_info.domain
        scopes = " ".join(oauth2_info.scopes)

        bfl_user = args.username
        bfl_user_password = args.password

        if "amazoncognito" not in domain:
            if args.bfm_https_cert is None:
                module_dir = os.path.dirname(__file__)
                cert = os.path.join(module_dir, "bfm_https_cert.pem")
            else:
                cert = args.bfm_https_cert
            access_token, refresh_token = domain_signin(
                domain, client_id, bfl_user, bfl_user_password, cert
            )
        else:
            access_token, refresh_token = get_cognito_access_token(
                domain, COGNITO_PORTS[0], client_id, scopes
            )

    user_info, license_info = set_cloud_tokens(api, access_token, refresh_token)
    log.info(f"set_cloud_tokens: {user_info}, {license_info}")

    user_info = get_user_info(api)
    log.info(f"get_user_info: {user_info}")

    return


if __name__ == "__main__":
    by_name["user-control"](False)


