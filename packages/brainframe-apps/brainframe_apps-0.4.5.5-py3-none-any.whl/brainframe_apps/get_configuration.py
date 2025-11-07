#
# Copyright (c) 2021 Dilili Labs, Inc.  All rights reserved. Contains Dilili Labs Proprietary Information. RESTRICTED COMPUTER SOFTWARE.  LIMITED RIGHTS DATA.
#
import json
import os
if __name__ == "__main__":
    os.environ['BF_LOG_PRINT'] = 'TRUE'

from argparse import ArgumentParser
from pathlib import Path

from brainframe.api import BrainFrameAPI, bf_errors
from brainframe_apps.command_utils import by_name, command, subcommand_parse_args
from brainframe_apps.list_stream import get_stream_persistent_id
from brainframe_apps.logger_factory import log


def get_stream_persistent_id_from_setting(setting):
    setting_connection_options = setting["stream_configurations"]["connection_options"]
    if "url" in setting_connection_options:
        setting_stream_persistent_id = setting_connection_options["url"]
    elif "storage_id" in setting_connection_options:
        setting_stream_persistent_id = setting_connection_options["storage_id"]
    elif "video_file_path" in setting_connection_options:
        setting_stream_persistent_id = setting_connection_options["video_file_path"]
    else:
        raise ValueError("no stream persistent id available")
    return setting_stream_persistent_id


def get_conf(video_file, setting_file, api):
    server_setting = {}

    if os.path.isfile(setting_file):
        with open(setting_file) as file:
            server_setting = json.load(file)

    capsules = api.get_capsules()

    # Save global capsules options
    if "global_capsule_options" not in server_setting:
        server_setting["global_capsule_options"] = {}

    if "global_capsule_active" not in server_setting:
        server_setting["global_capsule_active"] = {}

    for capsule in capsules:
        global_options = api.get_capsule_option_vals(capsule.name)
        server_setting["global_capsule_options"][capsule.name] = global_options
        server_setting["global_capsule_active"][capsule.name] = api.is_capsule_active(
            capsule_name=capsule.name
        )

    if "stream_settings" not in server_setting:
        server_setting["stream_settings"] = {}

    # Per stream settings
    stream_configurations = api.get_stream_configurations()
    for stream_configuration in stream_configurations:
        # Find the matching stream in settings
        for id, setting in server_setting["stream_settings"].items():
            if setting is not None:
                setting_stream_persistent_id = get_stream_persistent_id_from_setting(
                    setting
                )
                stream_persistent_id = get_stream_persistent_id(stream_configuration)
                if setting_stream_persistent_id == stream_persistent_id:
                    del server_setting["stream_settings"][id]
                    break

        # Save stream configurations
        stream_id = stream_configuration.id
        stream_configuration.id = None
        server_setting["stream_settings"][stream_id] = {}
        server_setting["stream_settings"][stream_id][
            "stream_configurations"
        ] = stream_configuration.to_dict()

        # If its video file, download the video file, and replace storage_id with file_path
        if stream_configuration.connection_type is stream_configuration.ConnType.FILE:
            log.debug(f"Saving Video file from server: {stream_configuration.name}")
            file_bytes, _ = api.get_storage_data(
                stream_configuration.connection_options["storage_id"]
            )
            if video_file:
                save_path = Path(video_file)
            else:
                save_path = Path(stream_configuration.name)

            with save_path.open("wb") as file:
                # file.write(file_bytes)
                pass
            del stream_configuration.connection_options["storage_id"]

            # notice that video_file_path is not a keyword of BrainFrame REST API
            stream_configuration.connection_options["video_file_path"] = str(
                save_path.absolute()
            )

        # Save zones and alarms
        zones = [zone.to_dict() for zone in api.get_zones(stream_id)]
        server_setting["stream_settings"][stream_id]["zones"] = zones

        server_setting["stream_settings"][stream_id]["stream_capsule_options"] = {}
        server_setting["stream_settings"][stream_id]["stream_capsule_active"] = {}

        # Save stream capsule options
        for capsule in capsules:
            stream_capsule_options = api.get_capsule_option_vals(
                capsule.name, stream_id=stream_id
            )
            server_setting["stream_settings"][stream_id]["stream_capsule_options"][
                capsule.name
            ] = stream_capsule_options
            stream_capsule_active = api.is_capsule_active(
                capsule_name=capsule.name, stream_id=stream_id
            )
            if stream_capsule_active is not None:
                server_setting["stream_settings"][stream_id]["stream_capsule_active"][
                    capsule.name
                ] = stream_capsule_active

    # Save Settings to file
    f = open(setting_file, "w")
    json.dump(server_setting, f, indent=4)
    f.close()


@command("save-settings")
def save_settings_main(is_command=True):
    parser = ArgumentParser(
        description="Save current BrainFrame server setting into a json file"
    )
    parser.add_argument(
        "--server-url",
        default="http://localhost",
        help="The BrainFrame server URL. Default: %(default)s",
    )
    parser.add_argument(
        "--setting-file",
        default="settings.json",
        help="File to store the server settings. Default: %(default)s",
    )
    parser.add_argument(
        "--video-file",
        default="video_file_name.mp4",
        help="Video file retrieved from BrainFrame server. Default: %(default)s",
    )
    args = subcommand_parse_args(parser, is_command)

    # Connect to BrainFrame server
    api = BrainFrameAPI(args.server_url)

    log.debug("{} Waiting for server at {} ...".format(parser.prog, args.server_url))
    try:
        api.wait_for_server_initialization(timeout=15)
    except (TimeoutError, bf_errors.ServerNotReadyError):
        log.debug(f"BrainFrame server connection timeout")
        return

    get_conf(args.video_file, args.setting_file, api)
    log.debug(f"Saved in {args.setting_file}")


if __name__ == "__main__":
    by_name["save-settings"](False)


