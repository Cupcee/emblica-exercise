import linecache
import os
import json
import argparse
import tracemalloc
from constants import GITHUB_PATH


def pp(session: dict):
    """Prettyprint dict into json."""
    if not all(
            k in session for k in {
                "user_id", "content_id", "session_start", "session_end",
                "total_time", "track_playtime", "event_count", "ad_count"
            }):
        raise Exception(session)
    json_str = json.dumps(session, indent=4)
    print(json_str)


def parse_args():
    """Return args for predict.py."""
    parser = argparse.ArgumentParser(description="Predict")
    parser.add_argument("--dataset",
                        type=str,
                        default="events.json",
                        choices=["events.json", "dataset2.json"],
                        help="The dataset to sessionize")
    parser.add_argument("--debug",
                        action="store_true",
                        help="Should print out number of sessions at end")
    parser.add_argument("--keep_file",
                        action="store_true",
                        help="Keep file after execute")
    return parser.parse_args()


def get_data_extract(dataset_name: str, file_type: str):
    """Get dataset from address "{GITHUB_PATH}/{dataset_name}."""
    if dataset_name in os.listdir():
        print(f"Dataset {dataset_name} already exists")
    else:
        print("Downloading the data...")
        if file_type == '.tar.gz':
            command = "tar xzvf"
            os.system(f"wget {GITHUB_PATH}/{dataset_name}{file_type}")
            print("Dataset downloaded!")
            print("Extracting data..")
            os.system(f"{command} {dataset_name}{file_type}")
            os.system(f"rm {dataset_name}{file_type}")
            print("Extraction done!")
        elif file_type == '.gz':
            command = "gzip -d"
            os.system(f"wget {GITHUB_PATH}/{dataset_name}{file_type}")
            print("Dataset downloaded!")
            print("Extracting data..")
            os.system(f"{command} {dataset_name}{file_type}")
            print("Extraction done!")
        else:
            raise Exception("Unknown datatype in dataset_name")


def display_top(snapshot, key_type='lineno', limit=3):
    """Print info about memory usage if taking a snapshot with tracemalloc."""
    snapshot = snapshot.filter_traces((
        tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
        tracemalloc.Filter(False, "<unknown>"),
    ))
    top_stats = snapshot.statistics(key_type)

    print("Top %s lines" % limit)
    for index, stat in enumerate(top_stats[:limit], 1):
        frame = stat.traceback[0]
        # replace "/path/to/module/file.py" with "module/file.py"
        filename = os.sep.join(frame.filename.split(os.sep)[-2:])
        print("#%s: %s:%s: %.1f KiB" %
              (index, filename, frame.lineno, stat.size / 1024))
        line = linecache.getline(frame.filename, frame.lineno).strip()
        if line:
            print('    %s' % line)

    other = top_stats[limit:]
    if other:
        size = sum(stat.size for stat in other)
        print("%s other: %.1f KiB" % (len(other), size / 1024))
    total = sum(stat.size for stat in top_stats)
    print("Total allocated size: %.1f KiB" % (total / 1024))
