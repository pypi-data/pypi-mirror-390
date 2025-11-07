#
# Copyright (c) 2021 Dilili Labs, Inc.  All rights reserved. Contains Dilili Labs Proprietary Information. RESTRICTED COMPUTER SOFTWARE.  LIMITED RIGHTS DATA.
#
import json
import os
if __name__ == "__main__":
    os.environ['BF_LOG_PRINT'] = 'TRUE'

from argparse import ArgumentParser

from brainframe.api import BrainFrameAPI, bf_errors
from brainframe.api.bf_codecs import StreamConfiguration, Zone
from brainframe_apps.command_utils import by_name, command, subcommand_parse_args
from brainframe_apps.get_configuration import get_stream_persistent_id_from_setting
from brainframe_apps.list_stream import get_stream_id
from brainframe_apps.logger_factory import log
from brainframe_apps.urls import UrlList, get_ip
from brainframe_apps.wait_for_ready import wait_for_capsule


def set_conf_global(local_video_file, stream_url, setting_file, api):
    # Load settings from config file
    with open(setting_file) as file:
        server_setting = json.load(file)

    load_global_capsule_options(server_setting, api)


def set_conf_stream(local_video_file, stream_persistent_id, setting_file, api):
    # Load settings from config file
    with open(setting_file) as file:
        server_setting = json.load(file)

    if "localhost" in stream_persistent_id:
        stream_persistent_id_for_server = stream_persistent_id.replace(
            "localhost", get_ip()
        )
    else:
        stream_persistent_id_for_server = stream_persistent_id

    log.debug(f"{stream_persistent_id_for_server}:")

    # Find the matching stream in settings
    stream_setting = None
    for _, setting in server_setting["stream_settings"].items():
        if (
            setting is not None
            and get_stream_persistent_id_from_setting(setting)
            == stream_persistent_id_for_server
        ):
            log.debug(f"    Found in {setting_file}")
            stream_setting = setting
            break

    if stream_setting is None:
        log.warning(f"    Not found in {setting_file}")

    stream_configuration = None

    # Find the matching stream from server
    if stream_setting is not None:

        stream_configuration_dict = stream_setting["stream_configurations"]
        stream_configuration = StreamConfiguration.from_dict(stream_configuration_dict)
        stream_id = get_stream_id(api, stream_persistent_id_for_server)
        if stream_id:
            # found a match on the server
            stream_configuration.id = stream_id

            load_stream_configuration(api, stream_configuration, stream_setting)
            log.debug(f"    Found on the server")
        else:
            log.debug(f"    Not found on the server")

    if stream_configuration is not None:
        stream_id = stream_configuration.id
    else:
        stream_id = None

    return stream_id


def load_global_capsule_options(server_setting, api):
    for capsule_name, capsule_options in server_setting[
        "global_capsule_options"
    ].items():
        # load settings will fail if the capsule has not been loaded to BrainFrame server
        wait_for_capsule(
            lambda: api.set_capsule_option_vals(
                capsule_name=capsule_name, option_vals=capsule_options
            ),
            capsule_name,
        )

    for capsule_name, capsule_active in server_setting["global_capsule_active"].items():
        # load settings will fail if the capsule has not been loaded to BrainFrame server
        wait_for_capsule(
            lambda: api.set_capsule_active(
                capsule_name=capsule_name, active=capsule_active
            ),
            capsule_name,
        )


def load_stream_configuration(api, stream_configuration, stream_setting):
    if stream_configuration is None:
        return

    stream_id = stream_configuration.id

    setup_zones_and_alarms(api, stream_id, stream_setting)

    setup_stream_capsule_configurations(api, stream_id, stream_setting)


def setup_zones_and_alarms(api, stream_id, stream_setting):
    zones = stream_setting["zones"]
    for zone_dict in zones:
        zone = Zone.from_dict(zone_dict)
        if zone.name != "Screen":
            zone.id = None
            zone.stream_id = stream_id
            for alarm in zone.alarms:
                alarm.id = None
                for count_condition in alarm.count_conditions:
                    count_condition.id = None
                for rate_condition in alarm.rate_conditions:
                    rate_condition.id = None
            try:
                api.set_zone(zone)

            except bf_errors.DuplicateZoneNameError as err:
                log.error(f"set_zone({zone.name}) failed: {str(err)}")

        else:
            try:
                screen_zone = [
                    zone for zone in api.get_zones(stream_id) if zone.name == "Screen"
                ][0]
                alarms = zone.alarms
                for alarm in alarms:
                    alarm.id = None
                    alarm.stream_id = stream_id
                    alarm.zone_id = screen_zone.id
                    for count_condition in alarm.count_conditions:
                        count_condition.id = None
                    for rate_condition in alarm.rate_conditions:
                        rate_condition.id = None
                    api.set_zone_alarm(alarm)
            except (
                bf_errors.ZoneNotFoundError,
                bf_errors.StreamConfigNotFoundError,
            ) as err:
                log.error(
                    f"get_zones({zone.name}), set_zone_alarm({alarm.name}) failed: {str(err)}"
                )


def setup_stream_capsule_configurations(api, stream_id, stream_setting):
    try:
        if "stream_capsule_options" in stream_setting.keys():
            for capsule_name, capsule_options in stream_setting[
                "stream_capsule_options"
            ].items():
                if capsule_name is not None:
                    wait_for_capsule(
                        lambda: api.set_capsule_option_vals(
                            stream_id=stream_id,
                            capsule_name=capsule_name,
                            option_vals=capsule_options,
                        ),
                        capsule_name,
                    )
        if "stream_capsule_active" in stream_setting.keys():
            for capsule_name, capsule_active in stream_setting[
                "stream_capsule_active"
            ].items():
                if capsule_name is not None:
                    wait_for_capsule(
                        lambda: api.set_capsule_active(
                            stream_id=stream_id,
                            capsule_name=capsule_name,
                            active=capsule_active,
                        ),
                        capsule_name,
                    )
    except (
        bf_errors.InvalidCapsuleError,
        bf_errors.StreamConfigNotFoundError,
        bf_errors.CapsuleNotFoundError,
    ) as err:
        log.error(
            f"set_capsule_option_vals({capsule_name}), set_capsule_active({capsule_name}) failed {str(err)}"
        )


def _set_configuration_parse_args(parser):
    parser.add_argument(
        "--server-url",
        default="http://localhost",
        help="The BrainFrame server URL. Default: %(default)s",
    )
    parser.add_argument(
        "--setting-file",
        default="settings.json",
        help="File to store the server settings",
    )
    parser.add_argument(
        "--stream-urls",
        default="stream-urls.csv",
        help="The name of the file with the list of stream urls. Default: %(default)s",
    )
    parser.add_argument(
        "--video-file", default=None, help="video file name. Default: %(default)s"
    )
    parser.add_argument(
        "--stream-url", default=None, help="The ip camera URL. Default: %(default)s"
    )


@command("load-settings")
def load_settings_main(is_command=True):
    parser = ArgumentParser(
        description="Load current BrainFrame server setting from a json file"
    )
    _set_configuration_parse_args(parser)
    args = subcommand_parse_args(parser, is_command)

    # Connect to BrainFrame server
    api = BrainFrameAPI(args.server_url)

    log.debug(f"{str(parser.prog)} Waiting for server at {args.server_url} ...")

    try:
        api.wait_for_server_initialization(timeout=15)
    except (TimeoutError, bf_errors.ServerNotReadyError):
        log.error(f"BrainFrame server connection timeout")
        return

    set_conf_global(None, None, args.setting_file, api)

    if args.stream_url is not None:
        stream_url = args.stream_url.replace("localhost", str(get_ip()))

        stream_id = set_conf_stream(args.video_file, stream_url, args.setting_file, api)
        if stream_id is not None:
            log.debug(f"Loading for {stream_url} has succeeded.")
        else:
            log.error(f"Loading for {stream_url} has failed.")
    else:
        # Try to use stream-urls.csv only if file exists
        if os.path.isfile(args.stream_urls):
            stream_urls = UrlList(args.stream_urls)
            if stream_urls:
                for stream_info in stream_urls:
                    stream_id = set_conf_stream(
                        args.video_file, stream_info.url, args.setting_file, api
                    )
                    if stream_id is not None:
                        log.debug(f"Loading for {stream_info.url} has succeeded.")
                    else:
                        log.error(f"Loading for {stream_info.url} has failed.")
            else:
                log.error(
                    "At least one of stream_url or stream_urls has to be provided"
                )
        else:
            log.error(
                "At least one of stream_url or stream_urls has to be provided"
            )


if __name__ == "__main__":
    by_name["load-settings"](False)


