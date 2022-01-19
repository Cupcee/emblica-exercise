import os
import json
from util import get_data_extract, parse_args, pp
from constants import HEARTBEAT_DURATION, TIMEOUT_DURATION, ALLOWED_EVENTS

# TODO: verify it works now
# TODO: try fetching data from url (with tarfile)
counter = 0
if __name__ == "__main__":
    args = parse_args()
    data = args.dataset
    get_data_extract(data, '.tar.gz' if data == "events.json" else ".gz")
    with open(data, 'r') as file:
        t0 = 0
        session = {}
        timeout = False
        for line in file:
            row = json.loads(line)
            event = row["event_type"]

            if event not in ALLOWED_EVENTS:
                continue

            t1 = int(row["timestamp"])  # current time
            td = 0 if t0 == 0 else t1 - t0  # difference to previous row
            t0 = t1

            session_timeout = td >= TIMEOUT_DURATION

            if session_timeout:
                timeout = True

            # if session has timed out, we wait for next stream start
            if timeout and event != "stream_start":
                counter += 1
                pp(session)
                continue

            if event == "stream_start":
                timeout = False
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
                counter += 1
                pp(session)
            else:
                session["total_time"] += td
                session["event_count"] += 1

    # Discard dataset if desired
    if args.discard:
        os.system(f"rm {data}")

print(counter)
