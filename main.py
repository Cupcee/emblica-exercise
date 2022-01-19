import os
import json
from util import get_data_extract, parse_args, pp
from constants import HEARTBEAT_DURATION, TIMEOUT_DURATION

allowed_events = {
    "stream_start", "ad_start", "ad_end", "track_start", "track_end",
    "track_heartbeat", "pause", "play", "track_end", "stream_end"
}

if __name__ == "__main__":
    args = parse_args()
    data = args.dataset
    get_data_extract(data, '.tar.gz' if data == "events.json" else ".gz")
    t0 = 0
    with open(data, 'r') as file:
        session = {}
        for line in file:
            row = json.loads(line)
            event = row["event_type"]

            if event not in allowed_events:
                continue

            t1 = int(row["timestamp"])  # current time
            td = 0 if t0 == 0 else t1 - t0  # difference to previous row
            t0 = t1

            session_timeout = td >= TIMEOUT_DURATION

            if event == "stream_start" and session_timeout:
                # we timeout so print to stdout
                pp(session)

                session = {
                    "user_id": row["user_id"],
                    "content_id": row["content_id"],
                    "session_start": row["timestamp"],
                    "total_time": 0,
                    "track_playtime": 0,
                    "event_count": 1,
                    "ad_count": 0,
                }
            if event == "stream_start":
                session = {
                    "user_id": row["user_id"],
                    "content_id": row["content_id"],
                    "session_start": row["timestamp"],
                    "total_time": 0,
                    "track_playtime": 0,
                    "event_count": 1,
                    "ad_count": 0,
                }
            elif event == "track_heartbeat":
                session["total_time"] += HEARTBEAT_DURATION
                session["track_playtime"] += HEARTBEAT_DURATION
                session["event_count"] += 1

            elif event == "ad_start":
                session["total_time"] += td
                session["event_count"] += 1
                session["ad_count"] += 1

            elif event == "pause":
                session["total_time"] += td
                session["event_count"] += 1
                session["track_playtime"] += td

            elif event == "stream_end":
                session["total_time"] += td
                session["event_count"] += 1
                pp(session)
            else:
                session["total_time"] += td
                session["event_count"] += 1

    # Discard dataset if desired
    if args.discard:
        os.system(f"rm {data}")
