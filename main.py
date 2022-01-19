import os
from util import get_data_extract, parse_args, pp
from constants import HEARTBEAT_DURATION, TIMEOUT_DURATION
import pandas as pd

if __name__ == "__main__":
    args = parse_args()
    data = args.dataset
    get_data_extract(data, '.tar.gz' if data == "events.json" else ".gz")
    with pd.read_json(
            data,
            lines=True,
            chunksize=args.chunksize,  # we read file in chunks to save memory
    ) as reader:

        # in case the last session of a previous chunk was not terminated
        # we save it here and add it to a new sessions list
        last_session = None
        t0 = 0
        for chunk in reader:
            sessions = [] if last_session is None else [last_session]

            for row in chunk.itertuples(index=False):
                # handle timestamp difference
                t1 = int(row.timestamp)  # current time
                td = 0 if t0 == 0 else t1 - t0  # difference to previous row
                t0 = t1

                event = row.event_type
                prev_session_closed = len(
                    sessions) > 0 and sessions[-1]["session_closed"]
                session_timeout = td > TIMEOUT_DURATION and not prev_session_closed

                if event == "stream_start" or session_timeout:

                    # if we timeout, output previous session to stdout
                    if session_timeout:
                        pp(sessions[-1])

                    # initalize new session
                    sessions.append({
                        "session_closed": False,
                        "user_id": row.user_id,
                        "content_id": row.content_id,
                        "session_start": row.timestamp,
                        "total_time": 0,
                        "track_playtime": 0,
                        "event_count": 1,
                        "ad_count": 0,
                    })

                elif event == "track_heartbeat":
                    session = sessions[-1]
                    session["total_time"] += HEARTBEAT_DURATION
                    session["track_playtime"] += HEARTBEAT_DURATION
                    session["event_count"] += 1

                else:
                    session = sessions[-1]
                    # for the rest of the events, always increment these
                    session["total_time"] += td
                    session["event_count"] += 1

                    if event == "ad_start":
                        session["ad_count"] += 1

                    elif event == "pause":
                        session["track_playtime"] += td

                    elif event == "stream_end":
                        session["session_closed"] = True
                        pp(sessions[-1])

            # save last session of the chunk in case its not terminated
            if not sessions[-1]["session_closed"]:
                last_session = sessions[-1]

    # Discard dataset if desired
    if args.discard:
        os.system(f"rm {data}")
