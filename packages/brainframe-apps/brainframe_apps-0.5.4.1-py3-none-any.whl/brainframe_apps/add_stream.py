#
# Copyright (c) 2021 Dilili Labs, Inc.  All rights reserved. Contains Dilili Labs Proprietary Information. RESTRICTED COMPUTER SOFTWARE.  LIMITED RIGHTS DATA.
#

import json
import os
if __name__ == "__main__":
    os.environ['BF_LOG_PRINT'] = 'TRUE'

import sys
from argparse import ArgumentParser
from pathlib import Path

from brainframe.api import BrainFrameAPI, bf_codecs, bf_errors
from brainframe.api.bf_codecs import StreamConfiguration
from brainframe_apps.command_utils import by_name, command, subcommand_parse_args
from brainframe_apps.list_stream import list_stream_parse_args
from brainframe_apps.logger_factory import log
from brainframe_apps.urls import UrlList


def add_stream(api, local_video_file, stream_url, stream_name=None, stream_options=None):
    """
    Add a stream to BrainFrame.
    
    Args:
        api: BrainFrame API instance
        local_video_file: Path to local video file (if any)
        stream_url: URL of the stream
        stream_name: Optional name for the stream (defaults to stream_url if not provided)
    
    Returns:
        StreamConfiguration or None
    """
    # Use stream_url as name if stream_name is not provided
    if stream_name is None:
        stream_name = stream_url

    # Initialize options dictionaries
    runtime_options = {}
    connection_options = {}

    # Parse JSON stream options if they exist
    if stream_options:
        try:
            # Load the JSON string into a Python dictionary
            parsed_options = json.loads(stream_options)

            # Pop "pipeline" into connection_options
            pipeline = parsed_options.pop("pipeline", None)
            if pipeline:
                connection_options["pipeline"] = pipeline
            
            # The rest of the parsed options are treated as runtime_options
            runtime_options.update(parsed_options)

        except json.JSONDecodeError:
            log.error(f"Invalid JSON format for stream options, ignoring: {stream_options}")

    if local_video_file:
        video_bytes = Path(local_video_file).read_bytes()
        storage_id = api.new_storage(data=video_bytes, mime_type="video/mp4")

        # Add storage_id to connection options for file streams
        connection_options["storage_id"] = storage_id

        stream_configuration_dict = bf_codecs.StreamConfiguration(
            name=local_video_file,
            premises_id=None,
            connection_type=bf_codecs.StreamConfiguration.ConnType.FILE,
            connection_options=connection_options,
            runtime_options=runtime_options,
            metadata={},
            id=None,
        ).to_dict()

        # Check if the StreamConfiguration is a video file, and upload the file if so
        # Notice that video_file_path is not a keyword from BrainFrame REST API, it is added
        # when we save the settings
        video_file_path_from_settings = stream_configuration_dict[
            "connection_options"
        ].get("video_file_path", None)

        if video_file_path_from_settings:
            if local_video_file:
                video_file_bytes = Path(local_video_file).read_bytes()
            else:
                video_file_bytes = Path(video_file_path_from_settings).read_bytes()

    else:
        # Add the stream URL to connection_options for IP cameras
        connection_options["url"] = stream_url

        stream_configuration_dict = bf_codecs.StreamConfiguration(
            name=stream_name,
            premises_id=None,
            connection_type=bf_codecs.StreamConfiguration.ConnType.IP_CAMERA,
            connection_options=connection_options,
            runtime_options=runtime_options,
            metadata={},
            id=None,
        ).to_dict()

    # Create StreamConfiguration
    stream_configuration = None

    try:
        sc = StreamConfiguration.from_dict(stream_configuration_dict)
        # log.debug(f'{__file__} {sc}')
        stream_configuration = api.set_stream_configuration(sc)
        log.debug(f"add_stream succeeded: {stream_configuration.id} {stream_url}")

    except (
        bf_errors.StreamNotOpenedError,
        bf_errors.DuplicateStreamSourceError,
        bf_errors.StreamConfigNotFoundError,
        bf_errors.InvalidRuntimeOptionError,
        bf_errors.UnknownError,
    ) as err:
        log.debug(f"add_stream failed {str(err)}: {stream_url}")

    return stream_configuration


@command("add-stream")
def add_stream_main(is_command=True):
    parser = ArgumentParser("This tool adds video streams to BrainFrame server.")
    list_stream_parse_args(parser)
    _add_stream_parse_args(parser)
    args = subcommand_parse_args(parser, is_command)

    # Connect to the BrainFrame Server
    server_url = args.server_url
    log.debug(
        f"{os.path.basename(sys.argv[0])} Waiting for BrainFrame server at '{server_url}'"
    )
    api = BrainFrameAPI(server_url)
    api.wait_for_server_initialization()

    if args.stream_url is not None:
        stream_url = args.stream_url
        # Use the --stream-name argument if provided
        stream_name = args.stream_name if hasattr(args, 'stream_name') and args.stream_name != "My video file" else None
        stream_configuration = add_stream(api, args.video_file, stream_url, stream_name)
    elif args.video_file is not None:
        stream_configuration = add_stream(api, args.video_file, None)
    else:
        # Try to use stream-urls.csv only if file exists
        if os.path.isfile(args.stream_urls):
            stream_urls = UrlList(args.stream_urls)
            if stream_urls:
                stream_configuration = None
                for stream_info in stream_urls:
                    # Use the name from CSV if provided, otherwise use URL
                    stream_configuration = add_stream(api, args.video_file, stream_info.url, stream_info.name, stream_info.json)
            else:
                log.debug(f"Read {args.stream_urls} failed")
        else:
            log.debug("No video source input")


def _add_stream_parse_args(parser):
    parser.add_argument(
        "--video-file",
        default=None,
        help="video file name. Default: %(default)s",
    )
    parser.add_argument(
        "--stream-name",
        default="My video file",
        help="The name of the automatically-generated BrainFrame stream",
    )
    parser.add_argument(
        "--stream-urls",
        default="stream-urls.csv",
        help="The name of the file with the list of stream urls. Default: %(default)s",
    )


if __name__ == "__main__":
    by_name["add-stream"](False)


