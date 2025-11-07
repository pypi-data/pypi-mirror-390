#
# Copyright (c) 2021 Dilili Labs, Inc.  All rights reserved. Contains Dilili Labs Proprietary Information. RESTRICTED COMPUTER SOFTWARE.  LIMITED RIGHTS DATA.
#
import fnmatch
import json
import os
if __name__ == "__main__":
    os.environ['BF_LOG_PRINT'] = 'TRUE'

import subprocess
import sys
from argparse import ArgumentParser
from pathlib import Path

from brainframe.api import BrainFrameAPI, bf_errors
from brainframe_apps.command_utils import by_name, command, subcommand_parse_args
from brainframe_apps.list_stream import list_stream, list_stream_parse_args, get_stream_id
from brainframe_apps.logger_factory import log
from brainframe_apps.wait_for_ready import wait_for_capsule
from brainframe_apps.urls import UrlList, get_ip

VISIONCAPSULES_EXT = ".cap"

capsule_name_filename_mapper = {
    # @todo
    # Need to create a separate mapping table for the public available capsules.
    # Making the capsule name same as the capsule file name could be a solution?
    #
    "classifier_safety_gear_openvino": "classifier_safety_gear_openvino.cap",
    "classifier_behavior_administration": "classifier_behavior_administration.cap",
    "detector_image_quality_administration": "detector_image_quality_administration.cap",
    "classifier_phoning": "classifier_phoning_elevator.cap",
    "detector_tablecard_administration": "detector_tablecard_administration.cap",
    "classifier_uniform_administration": "classifier_uniform_administration.cap",
    "detector_vehicle": "detector_vehicles_traffic.cap",
    "counter_work_factory": "counter_work_factory.cap",
    "encoder_person_accurate": "encoder_person_accurate.cap",
    "ALGORITHM_TYPE_FOR_CATEGORY_BEST_USE_OF_CAPSULE": "example_plugin.cap",
    "detector_face_openimages": "detector_face_open_images.cap",
    "aligner_face_openvino_advanced": "landmarks_face_openvino_advanced.cap",
    "detector_fake_customizable": "detector_fake.cap",
    "recognizer_face_bad": "recognizer_face_insightface.cap",
    "detector_gun": "detector_gun.cap",
    "tracker_person_low_framerate": "tracker_person_low_framerate.cap",
    "classifier_age": "classifier_age.cap",
    "classifier_behavior_closeup": "classifier_behavior_closeup.cap",
    "classifier_eyewear_closeup": "classifier_eyeware_closeup.cap",
    "classifier_gender_closeup": "classifier_gender_closeup.cap",
    "classifier_hat_administration": "classifier_hat_administration.cap",
    "classifier_vehicle_color": "classifier_vehicle_color.cap",
    "dtag": "detector_dtag.cap",
    "detector_fire_fast": "detector_fire.cap",
    "detector_license_plates": "detector_license_plate.cap",
    "detector_person_administration": "detector_person_administration.cap",
    "detector_person_and_vehicle_fast": "detector_person_and_vehicle_fast.cap",
    "detector_vehicle_license_plate_openvino": "detector_vehicle_license_plate_openvino.cap",
    "encoder_license_plate_openvino": "encoder_license_plate_openvino.cap",
    "encoder_person": "encoder_person.cap",
    "encoder_person_openvino": "encoder_person_openvino.cap",
    "landmarks_face_openvino_simple": "landmarks_face_openvino_simple.cap",
    "recognizer_face_landmarks_openvino": "recognizer_face_landmarks_openvino.cap",
    "tracker_person": "tracker_person_encoding.cap",
    "calculator_object_speed": "calculator_object_speed.cap",
    "detector_person_openvino": "detector_person_openvino.cap",
    "tracker_vehicle_iou": "tracker_vehicle_iou.cap",
    "detector_person_overhead_openvino": "detector_person_overhead_openvino.cap",
    "classifier_mask_closeup_openvino": "classifier_mask_closeup_openvino.cap",
    "detector_face_fast": "detector_face_fast.cap",
    "detector_safety_gear_openvino": "detector_safety_gear_openvino.cap",
    "classifier_person_attributes_openvino": "classifier_person_attributes_openvino.cap",
    "detector_text_openvino": "detector_text_openvino.cap",
    "detector_person_vehicle_bike_openvino": "detector_person_vehicle_bike_openvino.cap",
    "classifier_face_emotion_openvino": "classifier_face_emotion_openvino.cap",
    "detector_face_openvino": "detector_face_openvino.cap",
    "recognizer_face": "recognizer_face.cap",
    "classifier_face_age_gender_openvino": "classifier_face_age_gender_openvino.cap",
    "classifier_vehicle_color_openvino": "classifier_vehicle_color_openvino.cap",
    "classifier_pose_closeup": "classifier_pose_closeup.cap",
    "detector_customizable": "detector_customizable.cap",
    "detector_coco_80_mo": "detector_coco_80_mo.cap",
}

person_tracking_capsule_files = [
    "detector_person_openvino.cap",
    "encoder_person.cap",
    "tracker_person_encoding.cap",
]


def setup_person_tracking_capsule_bundle(api, stream_id=None, threshold=0.5):
    capsule_name = "detector_person_openvino"
    capsule_options = {
        "threshold": threshold,
        # "max_detection_overlap": 1.0,
        # "min_detection_area": 8000,
        # "max_detection_area": 99999999,
    }
    configure_capsule(api, capsule_name, capsule_options, stream_id)
    if stream_id is not None:
        enable_capsule(api, capsule_name, stream_id)

    capsule_name = "encoder_person"
    capsule_options = {"recognition_threshold": 0.2}
    configure_capsule(api, capsule_name, capsule_options, stream_id)
    if stream_id is not None:
        enable_capsule(api, capsule_name, stream_id)

    capsule_name = "tracker_person"
    capsule_options = {
        "min_confidence": 0.5,
        # "max_detection_overlap": 1.0,
        # "min_detection_height": 0,
        # "max_cosine_distance": 0.2,
        # "nn_budget": 50,
        # "distance_metric": "cosine",
        # "sticky_detections": False,
    }
    configure_capsule(api, capsule_name, capsule_options, stream_id)
    if stream_id is not None:
        enable_capsule(api, capsule_name, stream_id)


# This is a bad dependency to local brainframe server.
def get_local_vcap_dir():
    brainframe_info_data_path = subprocess.getoutput("brainframe info data_path")
    default_vcap_local_dir = brainframe_info_data_path + "/capsules"
    default_vcap_local_frig = brainframe_info_data_path + "/capsules_frig"

    return default_vcap_local_dir, default_vcap_local_frig


def find_localfiles(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
        break
    return result


def get_capsule_name(capsule_filename):
    try:
        capsule_name = list(capsule_name_filename_mapper.keys())[
            list(capsule_name_filename_mapper.values()).index(capsule_filename)
        ]
    except Exception as e:
        log.error(f"Exception {e}")
        capsule_name = None

    return capsule_name


def get_capsule_names(capsule_filenames):
    capsule_names = []
    for capsule_filename in capsule_filenames:
        # Map capsule name to capsule filename
        try:
            capsule_name = get_capsule_name(capsule_filename)
            capsule_names.append(capsule_name)
        except:
            log.error(f"{capsule_filename} not found")
    return capsule_names


def enable_capsule(api, capsule_name, stream_id=None):
    try:
        wait_for_capsule(
            lambda: api.set_capsule_active(
                capsule_name=capsule_name, stream_id=stream_id, active=True
            ),
            capsule_name,
        )
    except (bf_errors.ServerNotReadyError, Exception) as e:
        log.error(f" {e}: capsule_name: {capsule_name}, stream_id: {stream_id}")


def enable_all_capsules(api):
    if api:
        for capsule in api.get_capsules():
            enable_capsule(api, capsule.name)


def disable_capsule(api, capsule_name, stream_id=None):
    try:
        wait_for_capsule(
            lambda: api.set_capsule_active(
                capsule_name=capsule_name, stream_id=stream_id, active=False
            ),
            capsule_name,
        )
    except (bf_errors.ServerNotReadyError, Exception) as e:
        log.error(f" {e}: capsule_name: {capsule_name}, stream_id: {stream_id}")


def disable_all_capsules(api):
    if api:
        for capsule in api.get_capsules():
            disable_capsule(api, capsule.name)


def load_capsules(api, capsule_path, capsule_files):
    all_succeeded = True
    for capsule_file in capsule_files:
        if load_capsule(api, capsule_path + "/" + capsule_file) is not True:
            all_succeeded = False
    return all_succeeded


def load_capsule(api, capsule_filepath: Path):
    if not os.path.exists(capsule_filepath):
        return False

    with open(capsule_filepath, "rb") as f:
        try:
            new_storage_id = api.new_storage(f, "application/octet-stream")
            api.load_capsule(new_storage_id, "application/octet-stream")

            log.debug(f"Succeeded loading capsule: {capsule_filepath}")
        except bf_errors.CapsuleNotFoundError as e:
            log.warning(f"Failed to load capsule: {capsule_filepath}, error: {e}")
            return False
        except bf_errors.BaseAPIError as e:
            log.warning(f"Failed to load capsule: {capsule_filepath}, error: {e}")
            return False

    return True


def unload_capsules_with_filename(api, capsule_filepath_list=None):
    all_succeeded = True
    if capsule_filepath_list:
        for capsule_filepath in capsule_filepath_list:
            if unload_capsule_with_filename(api, capsule_filepath) is not True:
                all_succeeded = False
    else:
        try:
            capsules = api.get_capsules()
            for capsule in capsules:
                unload_capsule_with_capsule_name(api, capsule.name)
        except bf_errors.ServerNotReadyError:
            all_succeeded = False
            log.warning(
                f"A network exception occurred while communicating with the"
                "BrainFrame server"
            )
    return all_succeeded


def unload_capsule_with_filename(api, capsule_filepath: Path):
    capsule_filename = os.path.basename(capsule_filepath)
    capsule_name = get_capsule_name(capsule_filename)

    unload_capsule_with_capsule_name(api, capsule_name)


def unload_capsule_with_capsule_name(api, capsule_name):
    try:
        api.unload_capsule(capsule_name)
        log.debug(f"Succeeded unloading capsule: {capsule_name}")
    except bf_errors.CapsuleNotFoundError as err:
        log.warning(f"Failed to unload capsule: {capsule_name} {err}")
        return False
    except bf_errors.BaseAPIError as err:
        log.warning(f"Failed to unload capsule: {capsule_name}, {err}")
        return False

    return True


def configure_capsule(api, capsule_name, capsule_options, stream_id=None):
    wait_for_capsule(
        lambda: api.set_capsule_option_vals(
            capsule_name=capsule_name, stream_id=stream_id, option_vals=capsule_options
        ),
        capsule_name,
    )


def configure_capsule_no_wait(api, capsule_name, capsule_options):
    api.set_capsule_option_vals(capsule_name=capsule_name, option_vals=capsule_options)


def list_capsules(api):
    if api:
        capsules = api.get_capsules()
        log.debug(f"capsules on BrainFrame server: {api._server_url} {api.version()}:")
        for capsule in capsules:
            if api.is_capsule_active(capsule.name):
                capsule_status_flag = "Active"
            else:
                capsule_status_flag = "      "
            global_options = api.get_capsule_option_vals(capsule.name)
            json_string = json.dumps(global_options, separators=(",", ":"))
            log.debug(f"    * {capsule_status_flag} {capsule.name} {json_string}")
        return capsules


def _capsule_control_parse_args(parser):
    parser.add_argument(
        "--capsule-name",
        help="To control a capsule, a capsule name needs to be provided. Default: %(default)s"
        " applies to all capsules",
    )
    parser.add_argument(
        "--capsule-filename",
        default="detector_customizable.cap",
        help="To load a capsule, a capsule file needs to be provided",
    )
    parser.add_argument(
        "--options",
        default=None,
        help="To configure a capsule, the option needs to be provided",
    )
    parser.add_argument(
        "--stream-id", default=None, help="Specify a stream id. Default: %(default)s"
    )
    parser.add_argument(
        "--stream-urls",
        default="stream-urls.csv",
        help="The name of the file with the list of stream urls. Default: %(default)s",
    )
    parser.add_argument(
        "--cmd",
        default="list",
        help="list, enable, disable, load, unload or configure capsules. Default: %(default)s",
    )


@command("capsule-control")
def capsule_control_main(is_command=True):
    parser = ArgumentParser(
        description="This tool controls capsules of BrainFrame server."
    )
    list_stream_parse_args(parser)
    _capsule_control_parse_args(parser)
    args = subcommand_parse_args(parser, is_command)

    # Connect to the BrainFrame Server
    server_url = args.server_url if args.server_url else f"http://{args.server_url}"
    log.debug(
        f"{os.path.basename(sys.argv[0])} Waiting for BrainFrame server at {server_url}"
    )
    api = BrainFrameAPI(server_url)
    try:
        api.wait_for_server_initialization(timeout=15)
    except (TimeoutError, bf_errors.ServerNotReadyError):
        log.error(f"BrainFrame server connection timeout")
        return

    capsules = list_capsules(api)
    
    # Determine stream IDs from various sources
    stream_ids = []
    if args.stream_id is not None:
        stream_ids = [int(args.stream_id)]
    elif args.stream_url is not None:
        stream_url = args.stream_url.replace("localhost", str(get_ip()))
        stream_id = get_stream_id(api, stream_url)
        if stream_id is not None:
            stream_ids = [stream_id]
    else:
        # Try to use stream-urls.csv only if file exists
        if os.path.isfile(args.stream_urls):
            stream_urls = UrlList(args.stream_urls)
            if stream_urls:
                for stream_info in stream_urls:
                    stream_id = get_stream_id(api, stream_info.url)
                    if stream_id is not None:
                        stream_ids.append(stream_id)
    
    # If no stream IDs specified, use None (global operation)
    if not stream_ids:
        stream_ids = [None]
    
    if args.cmd == "list":
        list_stream(api, None, True)

    elif args.cmd == "disable":
        for stream_id in stream_ids:
            if args.capsule_name is None:
                for capsule in capsules:
                    disable_capsule(api, capsule.name, stream_id)
            else:
                disable_capsule(api, args.capsule_name, stream_id)

    elif args.cmd == "enable":
        for stream_id in stream_ids:
            if args.capsule_name is None:
                for capsule in capsules:
                    enable_capsule(api, capsule.name, stream_id)
            else:
                enable_capsule(api, args.capsule_name, stream_id)

    elif args.cmd == "load":
        load_capsule(api, Path(args.capsule_filename))

    elif args.cmd == "unload":
        if args.capsule_name is None:
            for capsule in capsules:
                unload_capsule_with_capsule_name(api, capsule.name)
        else:
            unload_capsule_with_capsule_name(api, args.capsule_name)

    elif args.cmd == "configure":
        for stream_id in stream_ids:
            if args.options is None:
                capsule_options = {
                    "detector_class_name": "person",
                    "number_of_detections": 1,
                    "number_of_tracked_detection": 0,
                    "max_width": -1,
                    "batch_predict_latency": 0.0,
                    "process_frame_latency": 0.0,
                    "log_stream_performance": False,
                    "stream_fps_samples": 30,
                }
                configure_capsule(api, args.capsule_name, capsule_options, stream_id)
            else:
                capsule_options = json.loads(args.options)
                configure_capsule(api, args.capsule_name, capsule_options, stream_id)

    elif args.cmd == "load_person_bundle":
        load_capsules(api, ".", person_tracking_capsule_files)

    elif args.cmd == "setup_person_bundle":
        for stream_id in stream_ids:
            setup_person_tracking_capsule_bundle(api, stream_id, 0.5)


if __name__ == "__main__":
    by_name["capsule-control"](False)


