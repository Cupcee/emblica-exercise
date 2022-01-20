import os
import json
from util import get_data_extract, parse_args, pp
from constants import HEARTBEAT_DURATION, TIMEOUT_DURATION, ALLOWED_EVENTS

if __name__ == "__main__":
    args = parse_args()
    data = args.dataset
    get_data_extract(data, '.tar.gz' if data == "events.json" else ".gz")
    with open(data, 'r') as file:
        t0 = 0
        counter = 0
        session = {}
        timeout = False
        for line in file:
            row = json.loads(line)
            event = row["event_type"]

            # if we see unknown events, disregard them
            if event not in ALLOWED_EVENTS:
                continue

            t1 = int(row["timestamp"])  # current time
            td = 0 if t0 == 0 else t1 - t0  # difference to previous row

            # if time difference to previous event is too large we timeout
            timeout = td >= TIMEOUT_DURATION

            if timeout:
                # previous session ends at its final timestamp
                session["session_end"] = t0
                if args.debug:
                    counter += 1
                pp(session)

            # update previous to current for next iteration
            t0 = t1

            # we initialize new session either if stream_start is observed
            # or if last session timeouts
            if event == "stream_start" or timeout:
                session = {
                    "user_id": row["user_id"],
                    "content_id": row["content_id"],
                    "session_start": row["timestamp"],
                    "session_end": 0,
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
                # session ends at current timestamp
                session["session_end"] = t1
                if args.debug:
                    counter += 1
                pp(session)
            else:
                session["total_time"] += td
                session["event_count"] += 1

    # Discard dataset if desired
    if not args.keep_file:
        os.system(f"rm {data}")

    if args.debug:
        print(counter)
