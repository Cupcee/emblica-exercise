Prerequisites without Docker:
* Python 3 
  * 3.8.12 tested
  * likely has to be newer than ~3.4
* Tested on macOS Monterey 
* It uses `wget` to fetch the datasets from URL, so without docker you need it to run in command line

To run, either:
* run `python main.py`
  * Runs the larger dataset `events.json` by default
    * To choose between the datasets, use `--dataset [dataset_name]`, see `--help` for options
  * On first run the dataset used is downloaded to the project root
    * Dataset is discarded after run by default, use `--keep_file` to keep it in project root

Or, with Docker:
* `docker build --tag [some_name] .`
* `docker run [some_name] [your_args]` (see args above)

__Note__: The solution simply prints results to `stdout` as requested. No actual log file of the results is written
as that was no requested, but would be simple to add into the solution.
