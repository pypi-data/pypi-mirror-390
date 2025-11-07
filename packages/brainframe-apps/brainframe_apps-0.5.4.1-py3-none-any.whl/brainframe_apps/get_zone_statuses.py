#
# Copyright (c) 2021 Dilili Labs, Inc.  All rights reserved. Contains Dilili Labs Proprietary Information. RESTRICTED
# COMPUTER SOFTWARE.  LIMITED RIGHTS DATA.
#
import os
if __name__ == "__main__":
    os.environ['BF_LOG_PRINT'] = 'TRUE'

import json
import sys
import threading
from argparse import ArgumentParser
from collections import Counter
from datetime import datetime
from threading import Thread
from time import time

from brainframe.api import BrainFrameAPI, bf_errors
from brainframe_apps.command_utils import by_name, command, subcommand_parse_args
from brainframe_apps.fps_report import calc_fresh_tstamp_fps, collect_tstamps
from brainframe_apps.logger_factory import log


class GetZoneStatuses(Thread):
    def __init__(self, api: BrainFrameAPI, times_hist_len, stream_id):

        self.api = api
        self.EXIT = False
        self.times_hist_len = times_hist_len
        self.stream_id = stream_id

        self.stop = threading.Event()
        Thread.__init__(self, daemon=True)

    def run(self):
        try:
            self.get_zone_statuses(self.api, self.stream_id)
        finally:
            pass

    def get_zone_statuses_start(self):
        self.start()

    def get_zone_statuses_stop(self):
        self.EXIT = True
        self.stop.set()

    def get_zone_statuses_wait(self):
        self.join()

    def output_info(
        self,
        index=None,
        zs_time=None,
        time_elapse=None,
        api_iter_time=None,
        app_iter_time=None,
        call_per_sec=None,
        fps_throughput=None,
        all_frame_per_sec=None,
        stream_id=None,
        drift=None,
        dsync=None,
        tstamp=None,
        detections=None,
    ):
        if type(stream_id) is int:
            timestamp = datetime.fromtimestamp(tstamp)
            if fps_throughput is not None:
                fps_throughput_str = f"{fps_throughput:6.02f}"
            else:
                fps_throughput_str = "      "

            text = f"{str(index or ''):>5}: {zs_time}] {time_elapse:5.02f} {int(call_per_sec):6.02f}/{all_frame_per_sec:6.02f}/{fps_throughput_str} {api_iter_time:.03f}/{app_iter_time:.03f}"
            stream_text = (
                f"{stream_id:5}] {dsync:6.02f}/{drift:6.02f} [{timestamp}] {detections}"
            )
            if index is not None:
                log.debug(f"{text} {stream_text}")
            else:
                log.debug(f"{' ' * len(text)} {stream_text}")

        else:
            log.debug(
                f"index: {'time':>26}] elapse cps/fps/throughput  api/app_time s_id]  dsync/drift  [{'timestamp':>26}] [{'detections':13}]"
            )

    def get_zone_statuses(self, api, input_stream_id):
        # Start the clock
        tstamp_0 = None
        zs_time_0 = None
        last_start_time = datetime.now()
        last_end_time = last_start_time
        index = 0
        total_samples = 0
        times_hist = {}
        try:
            for zone_statuses in api.get_zone_status_stream(timeout=5):
                zs_time = datetime.now()
                times_hist, tstamp_hist_0, is_empty = collect_tstamps(
                    times_hist,
                    self.times_hist_len,
                    zone_statuses,
                    zs_time.timestamp(),
                )
                if is_empty:
                    continue

                if zs_time_0 is None:
                    zs_time_0 = zs_time
                    self.output_info()
                    log.debug(f"{index:>5}: {zs_time_0}] Start")

                if tstamp_0 is None:
                    if tstamp_hist_0 is not None:
                        tstamp_0 = tstamp_hist_0
                    else:
                        continue

                api_iter_time = (zs_time - last_end_time).total_seconds()
                app_iter_time = (last_end_time - last_start_time).total_seconds()

                total_samples += len(zone_statuses)
                time_elapse = (zs_time - zs_time_0).total_seconds()
                index += 1
                if time_elapse < 1:
                    call_per_sec = index
                    all_frame_per_sec = total_samples
                else:
                    call_per_sec = index / time_elapse
                    all_frame_per_sec = total_samples / time_elapse

                (
                    fps_throughput,
                    _,
                    _,
                    _,
                    fps_buf_age_dsync_drift,
                ) = calc_fresh_tstamp_fps(
                    times_hist, tstamp_0, zs_time_0, zone_statuses, zs_time.timestamp()
                )

                index_print = index
                for stream_id, zone_status in zone_statuses.items():

                    if self.EXIT:
                        log.debug(f"{index:>5}: {zs_time}] End")
                        self.output_info()
                        return

                    stream_id = zone_status["Screen"].zone.stream_id
                    tstamp = zone_status["Screen"].tstamp

                    within = zone_status["Screen"].within
                    count_each_class = Counter(
                        detection.class_name
                        for detection in within
                        if detection.class_name
                    )
                    unique_names = sorted(count_each_class.items())

                    tstamp_elapse = tstamp - tstamp_0
                    drift = tstamp_elapse - time_elapse
                    dsync = zs_time.timestamp() - tstamp
                    if input_stream_id is None or (
                        input_stream_id is not None and input_stream_id == stream_id
                    ):
                        self.output_info(
                            index_print,
                            zs_time,
                            time_elapse,
                            api_iter_time,
                            app_iter_time,
                            call_per_sec,
                            fps_throughput,
                            all_frame_per_sec,
                            stream_id,
                            drift,
                            dsync,
                            tstamp,
                            f"{unique_names}",
                        )
                    index_print = None

                last_start_time = zs_time
                last_end_time = datetime.now()

        except bf_errors.ServerNotReadyError:
            log.error(f"BrainFrame server error: bf_errors.ServerNotReadyError.")

        except json.decoder.JSONDecodeError:
            log.error("BrainFrame server error: json.decoder.JSONDecodeError")


def _get_zone_statuses_parse_args(parser):
    parser.add_argument(
        "--server-url",
        default="http://localhost",
        help="The BrainFrame server URL. Default: %(default)s",
    )
    parser.add_argument(
        "--stream-id", default=None, help="Specify a stream id. Default: %(default)s"
    )
    parser.add_argument(
        "--n-samples",
        default=100,
        help="Number of fresh fps tstamp samples to cache. Default: %(default)s",
    )


@command("get-zone-statuses")
def get_zone_statuses_main(is_command=True):
    parser = ArgumentParser(
        description="This tool gets zone events in videos from BrainFrame Server"
    )
    _get_zone_statuses_parse_args(parser)
    args = subcommand_parse_args(parser, is_command)

    api = BrainFrameAPI(args.server_url)

    log.debug("{} Waiting for server at {} ...".format(parser.prog, args.server_url))
    try:
        api.wait_for_server_initialization()
    except (TimeoutError, bf_errors.ServerNotReadyError):
        sys.exit("BrainFrame server connection timeout")

    if args.stream_id != None:
        stream_id = int(args.stream_id)
    else:
        stream_id = None
    GZS = GetZoneStatuses(api, args.n_samples, stream_id)
    GZS.get_zone_statuses_start()

    input("Press Enter to exit\n")
    GZS.get_zone_statuses_stop()
    GZS.get_zone_statuses_wait()

    api.close()

    print("Enter is pressed. Exit.")


if __name__ == "__main__":
    by_name["get-zone-statuses"](False)


