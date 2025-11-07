#
# Copyright (c) 2021 Dilili Labs, Inc.  All rights reserved. Contains Dilili Labs Proprietary Information. RESTRICTED COMPUTER SOFTWARE.  LIMITED RIGHTS DATA.
#
import json
import os
if __name__ == "__main__":
    os.environ['BF_LOG_PRINT'] = 'TRUE'

from argparse import ArgumentParser

from brainframe.api import BrainFrameAPI, bf_errors
from brainframe_apps.command_utils import by_name, command, subcommand_parse_args
from brainframe_apps.list_stream import get_stream_persistent_id
from brainframe_apps.logger_factory import log
from brainframe_apps.urls import UrlList, get_ip


def start_analyzing(api, stream_url):
    stream_id = analyzing_on_off_persistent_id(api, stream_url, True, False)

    if stream_id is not None:
        log.debug(f"{os.path.basename(__file__)}: {stream_url} succeeded: {stream_id}")
    else:
        log.error(f"{os.path.basename(__file__)}: {stream_url} failed")

    return stream_id


def analyzing_on_off_persistent_id(
    api, stream_persistent_id, analyzing_on, keyframe_only
):
    if stream_persistent_id is None:
        return None

    stream_id = None
    try:
        streams = api.get_stream_configurations()

        for stream in streams:
            server_stream_persistent_id = get_stream_persistent_id(stream)
            if stream_persistent_id == str(server_stream_persistent_id):
                _analyzing_on_off(api, stream.id, analyzing_on, keyframe_only)
                stream_id = stream.id
                break

    except (bf_errors.ServerNotReadyError, json.decoder.JSONDecodeError) as e:
        log.error(f"{e}")

    return stream_id


def _analyzing_on_off(api, stream_id, analyzing_on, keyframe_only):
    if analyzing_on is True:
        try:
            api.set_runtime_option_vals(stream_id, {"keyframes_only": keyframe_only})
        except:
            # ignore errors if the runtime option is not supported by the stream
            pass
        is_analyzing = api.check_analyzing(stream_id, timeout=30)
        if not is_analyzing:
            api.start_analyzing(stream_id)
            pass
    else:
        is_analyzing = api.check_analyzing(stream_id, timeout=30)
        if is_analyzing:
            api.stop_analyzing(stream_id)
            pass


def start_analyzing_parse_args(parser):
    parser.add_argument(
        "--server-url", default="http://localhost", help="The BrainFrame server URL"
    )
    parser.add_argument("--stream-url", default=None, help="stream-url to turn on/off")
    parser.add_argument(
        "--keyframe-only",
        dest="keyframe_only",
        action="store_true",
        default=False,
        help="Enable keyframe only streaming",
    )


def _start_analyzing_parse_args(parser):
    parser.add_argument(
        "--stream-urls",
        default="stream-urls.csv",
        help="The name of the file with the list of stream urls. Default: %(default)s",
    )


def start_analyzing_all(api):
    analyzing_on_off_all(api, True)


def analyzing_on_off_all(api, analyzing_on):
    streams = api.get_stream_configurations()

    stream_id = None
    stream = None
    for stream in streams:
        try:
            _analyzing_on_off(api, stream.id, analyzing_on, False)
        except Exception as e:
            log.error(f"Exception {e}")


@command("start-analyzing")
def start_analyzing_main(is_command=True):
    parser = ArgumentParser(description="Start analyze a BrainFrame video stream")
    start_analyzing_parse_args(parser)
    _start_analyzing_parse_args(parser)
    args = subcommand_parse_args(parser, is_command)

    # Connect to BrainFrame server
    api = BrainFrameAPI(args.server_url)

    log.debug(f"{str(parser.prog)} Waiting for server at {args.server_url} ...")

    try:
        api.wait_for_server_initialization(timeout=15)
    except (TimeoutError, bf_errors.ServerNotReadyError):
        log.error(f"BrainFrame server connection timeout")
        return

    # Handle single stream-url or stream-urls.csv
    if args.stream_url is not None:
        stream_url = args.stream_url.replace("localhost", str(get_ip()))
        stream_id = start_analyzing(api, stream_url)
    else:
        # Try to use stream-urls.csv only if file exists
        if os.path.isfile(args.stream_urls):
            stream_urls = UrlList(args.stream_urls)
            if stream_urls:
                for stream_info in stream_urls:
                    stream_id = start_analyzing(api, stream_info.url)
            else:
                # File exists but is empty/invalid
                log.error(f"No stream specified")
        else:
            # No stream_url and no CSV file, start all streams
            start_analyzing_all(api)


if __name__ == "__main__":
    by_name["start-analyzing"](False)


