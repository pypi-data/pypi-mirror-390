#
# Copyright (c) 2021 Dilili Labs, Inc.  All rights reserved. Contains Dilili Labs Proprietary Information. RESTRICTED COMPUTER SOFTWARE.  LIMITED RIGHTS DATA.
#
import os
if __name__ == "__main__":
    os.environ['BF_LOG_PRINT'] = 'TRUE'

import sys
from argparse import ArgumentParser
from time import sleep

import numpy
from brainframe.api import BrainFrameAPI
from brainframe_apps.capsule_control import get_capsule_names
from brainframe_apps.command_utils import by_name, command, subcommand_parse_args
from brainframe_apps.logger_factory import log
from brainframe_apps.time_utils import Timeout
from matplotlib import pyplot as plt
from PIL import Image


def process_video(api):
    timeout = Timeout(60, print_timeout=True)
    for zone_status_packet in api.get_zone_status_stream(timeout):
        for stream_id, zone_statuses in zone_status_packet.items():

            for detection in zone_statuses.within:
                log.debug(detection)
        sleep(0.001)


def process_image(api, capsule_names, img_bgr):
    detections = api.process_image(img_bgr, capsule_names, {})

    return detections


def draw_detection(ax, detection):
    coords = detection.coords

    x0, y0 = coords[0]
    x1, y1 = coords[1]
    x2, y2 = coords[2]
    w = x2 - x0
    h = y2 - y0

    if detection.class_name == "person":
        rect = plt.Rectangle(
            (x0, y0), w, h, edgecolor="yellow", linewidth=1, facecolor="none"
        )
        ax.add_patch(rect)
    elif detection.class_name == "face":
        rect = plt.Rectangle((x0, y0), w, h, color="yellow", alpha=0.25)
        ax.add_patch(rect)
    elif detection.class_name == "face_landmarks":
        coords.append(coords[0])
        xs, ys = zip(*coords)
        ax.plot(xs, ys, "red")
    else:
        rect = plt.Rectangle(
            (x0, y0), w, h, edgecolor="red", linewidth=1, facecolor="red"
        )
        ax.add_patch(rect)

    label = f"{detection.class_name}"
    if "detection_confidence" in detection.extra_data:
        label += f":{float(detection.extra_data['detection_confidence']):0.2f}"
    if detection.with_identity:
        if detection.with_identity.unique_name is not None:
            label += f" {detection.with_identity.unique_name}"
        if detection.with_identity.nickname is not None:
            label += f" ({detection.with_identity.nickname})"
        if "encoding_distance" in detection.extra_data:
            label += f"{float(detection.extra_data['encoding_distance']):0.2f}"

    ax.text(x0, y0, label, verticalalignment="top", multialignment="left", color="blue")


def _process_image_parse_args(parser):
    parser.add_argument(
        "--server-url",
        default="http://localhost",
        help="The URL for the BrainFrame server.",
    )
    parser.add_argument(
        "--image-path",
        default=None,
        required=True,
        help="PNG image file name for processing.",
    )


def load_image_and_process(api, image_path, capsule_files):
    image_pillow = Image.open(image_path)
    image_bgr = numpy.array(image_pillow)
    # image_data = args.image_path.read_bytes()

    capsule_names = get_capsule_names(capsule_files)

    detections = process_image(api, capsule_names, image_bgr)
    return detections, image_bgr


@command("process-image")
def process_image_main(is_command=True):
    parser = ArgumentParser(
        "This tool will control BrainFrame server to analyze an image."
    )
    _process_image_parse_args(parser)
    args = subcommand_parse_args(parser, is_command)

    # Connect to the BrainFrame Server
    server_url = args.server_url
    log.debug(
        f"{os.path.basename(sys.argv[0])} Waiting for BrainFrame server at '{server_url}'"
    )
    api = BrainFrameAPI(server_url)
    api.wait_for_server_initialization()

    capsule_files = [  # @todo
        "encoder_person_openvino.cap",
        "detector_person_openvino.cap",
        # "detector_face_openvino.cap",
        # "landmarks_face_openvino_simple.cap",
        # "recognizer_face_landmarks_openvino.cap",
        "tracker_person_encoding.cap",
        # "detector_face_fast.cap",
        # "recognizer_face.cap",
    ]

    log.debug("Press q on the new window to Exit")
    detections, image_bgr = load_image_and_process(api, args.image_path, capsule_files)

    fig, axs = plt.subplots(1, 1)
    axs.imshow(image_bgr)
    for detection in detections:
        log.debug(f"detection: {detection}")
        draw_detection(axs, detection)

    plt.show()


if __name__ == "__main__":
    by_name["process-image"](is_command=False)


