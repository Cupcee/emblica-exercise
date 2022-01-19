Prerequisites:
* Python 3 
  * 3.8.12 tested
  * likely has to be newer than ~3.4 because I import `tracemalloc` for memory usage stats
* `pip`

To run:
* run `pip install -r requirements.txt`
* run `python main.py`
  * Runs the larger dataset `events.json` by default
  * On first run the dataset used is downloaded to the project root
  * To choose between the datasets, use `--dataset [dataset_name]`, see `--help` for options
  * Can also use different chunk/batch size with `--chunksize [int]`

__Note__: The solution simply prints results to `stdout` as requested. No actual log file of the results is written
as that was no requested, but would be simple to add into the solution.
