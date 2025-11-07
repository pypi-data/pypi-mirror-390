#
# Copyright (c) 2022 Dilili Labs, Inc.  All rights reserved. Contains Dilili Labs Proprietary Information. RESTRICTED
# COMPUTER SOFTWARE.  LIMITED RIGHTS DATA.
#


def collect_tstamps(times_hist, times_hist_len, zone_statuses, zs_time):
    # brainframe-api v0.30.0 will return {} when zone_statuses is empty.
    if len(zone_statuses) == 0:
        is_empty = True
        return times_hist, None, is_empty
    else:
        is_empty = False

    # Remove keys from the times dict for stream ids that have been deleted
    # brainframe-api v0.30.0 will return {} when zone_statuses is empty, so
    # may not be able to remove the key for the last stream
    existing_stream_ids = set(s_id for s_id in zone_statuses.keys())
    times_hist = {
        s_id: times for s_id, times in times_hist.items() if s_id in existing_stream_ids
    }

    zs_tstamp_hist_0 = None

    for stream_id, zs in zone_statuses.items():
        if "Screen" not in zs:
            continue
        zs_tstamp = zs["Screen"].tstamp

        if stream_id not in times_hist:
            # This is the first result, it is definitely new.
            times_hist[stream_id] = [(zs_tstamp, zs_time)]
            if zs_tstamp_hist_0 is None:
                zs_tstamp_hist_0 = zs_tstamp
        else:
            zs_tstamp_hist_1, zs_time_hist_1 = times_hist[stream_id][-1]
            if zs_tstamp_hist_1 < zs_tstamp:
                # This is a fresh result, so it should be recorded.
                times_hist[stream_id].append((zs_tstamp, zs_time))
            else:
                # Same tstamp is discarded
                pass

        # Limit the length of times_hist
        times_hist[stream_id] = times_hist[stream_id][-times_hist_len:]
    return times_hist, zs_tstamp_hist_0, is_empty


def calc_fresh_tstamp_fps(times_hist, tstamp_0, time_0, zone_statuses, zs_time):
    # Create the overall stream throughput report
    stream_fps = []
    stream_ids = []
    fps_buf_age_dsync_drift = {}
    for stream_id, stream_times in times_hist.items():
        if len(stream_times) <= 0:
            continue
        n_samples = len(times_hist[stream_id])
        zs_tstamp_hist_0, zs_time_hist_0 = stream_times[0]
        zs_tstamp_hist_1, zs_time_hist_1 = stream_times[-1]
        buffered = zs_time_hist_1 - zs_time_hist_0
        if buffered > 0:
            fps = n_samples / buffered
        else:
            fps = n_samples

        age = zs_time - zs_time_hist_1
        dsync = zs_time_hist_1 - zs_tstamp_hist_1
        time_elapse = zs_time_hist_1 - time_0.timestamp()
        tstamp_elapse = zs_tstamp_hist_1 - tstamp_0
        drift = tstamp_elapse - time_elapse

        fps_buf_age_dsync_drift[stream_id] = {}
        fps_buf_age_dsync_drift[stream_id]["buf"] = buffered
        fps_buf_age_dsync_drift[stream_id]["age"] = age
        fps_buf_age_dsync_drift[stream_id]["dsync"] = dsync
        fps_buf_age_dsync_drift[stream_id]["drift"] = drift

        if (stream_id in zone_statuses) and (age < buffered):
            fps_buf_age_dsync_drift[stream_id]["fps"] = fps
            stream_fps.append(fps)
            stream_ids.append(stream_id)
        else:
            fps_buf_age_dsync_drift[stream_id]["fps"] = 0

    if not len(stream_fps):
        throughput_fps = None
        avg_fps = None
        max_fps = None
        min_fps = None

        max_sid = None
        min_sid = None
    else:
        throughput_fps = sum(stream_fps)
        avg_fps = sum(stream_fps) / len(stream_fps)
        max_fps = max(stream_fps)
        min_fps = min(stream_fps)

        max_sid = stream_ids[stream_fps.index(max_fps)]
        min_sid = stream_ids[stream_fps.index(min_fps)]

    return (
        throughput_fps,
        avg_fps,
        (max_fps, max_sid),
        (min_fps, min_sid),
        fps_buf_age_dsync_drift,
    )


def format_fresh_tstamp_fps_report(throughput_fps, avg_fps, max_fps_t, min_fps_t):
    if throughput_fps is None:
        throughput_fps_str = "..."
        avg_fps_str = "..."
        max_fps_str = "..."
        min_fps_str = "..."

        max_sid = "..."
        min_sid = "..."
    else:
        max_fps, max_sid = max_fps_t
        min_fps, min_sid = min_fps_t

        throughput_fps_str = f"{round(throughput_fps, 2)}"
        avg_fps_str = f"{round(avg_fps, 2)}"
        max_fps_str = f"{round(max_fps, 2)}"
        min_fps_str = f"{round(min_fps, 2)}"

    stream_fps_summary_header = [
        "FPS THROUGHPUT",
        "AVG STREAM",
        f"MAX: {max_sid}",
        f"MIN: {min_sid}",
    ]
    stream_fps_summary = [throughput_fps_str, avg_fps_str, max_fps_str, min_fps_str]
    return stream_fps_summary_header, stream_fps_summary, throughput_fps_str
