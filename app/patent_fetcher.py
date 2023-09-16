import json
import os
import time
from io import BytesIO
from multiprocessing import Manager, Pool
from typing import Optional, Tuple

import pandas as pd
import pycurl

try:
    from app.custom_logging import get_logger
except:
    from custom_logging import get_logger

my_logger = get_logger("uspto_bulk_search_download")
# Constants should be all caps
output_folder = "data"
os.makedirs(output_folder, exist_ok=True)
API_URL = "https://developer.uspto.gov/ibd-api/v1/application/grants"


# Not using correct PEP8 python styinlg for class name.
class uspto_bulk_search:
    def __init__(self, grantFromDate: str, grantToDate: str, rows: int) -> None:
        """Initialize a USPTO Bulk Search object.

        Args:
            grantFromDate: The starting date for patent grants in the format 'YYYY-MM-DD'.
            grantToDate: The ending date for patent grants in the format 'YYYY-MM-DD'.
            rows: The number of rows to request per API call.
        """
        self.grantFromDate = grantFromDate
        self.grantToDate = grantToDate
        self.rows = rows

    def request_data(self, start_size: int, results_dict: Optional[dict] = None):
        """Make a request to the USPTO API to retrieve patent data.

        Args:
            start_size: The starting index for the API request.
            results_dict: A shared dictionary for storing the retrieved results.

        Returns:
            list or None: A list of dictionaries containing patent data or None if no results are found.
        """
        url = f"{API_URL}?grantFromDate={self.grantFromDate}1&start={start_size}&grantToDate={self.grantToDate}&rows={self.rows}"

        c = pycurl.Curl()
        data = BytesIO()

        try:
            c.setopt(c.URL, url)
            c.setopt(c.SSL_VERIFYPEER, 0)
            c.setopt(c.SSL_VERIFYHOST, 0)
            c.setopt(c.WRITEFUNCTION, data.write)
            c.perform()
            response_code = c.getinfo(c.RESPONSE_CODE)
            my_logger.info(f"process response code: {response_code}")
            if response_code == 200:
                dictionary = json.loads(data.getvalue())
                if dictionary.get("results"):
                    fields = [
                        "patentNumber",
                        "patentApplicationNumber",
                        "assigneeEntityName",
                        "filingDate",
                        "grantDate",
                        "inventionTitle",
                    ]
                    results = [
                        {field: patent[field] for field in fields}
                        for patent in dictionary["results"]
                    ]
                    results_dict[
                        start_size
                    ] = results  # Store results in the shared dictionary
                else:
                    my_logger.error(f"No results for start in process: {start_size}")
                    return None
                    # return None
            elif response_code == 403:
                my_logger.error(f"Failed start in process: {start_size}")
                time.sleep(20)
                return self.request_data(start_size)  # Retry
            else:
                my_logger.error(f"Failed start in process: {start_size}")
                return []
        except Exception as e:
            my_logger.error(f"Error in process {start_size}: {e}")
            return []
        finally:
            c.close()

    # Define a separate function for mapping to work around pickling issue
    def map_request_data(self, args: Tuple[int, Optional[dict]]):
        """Map function for parallel processing of request_data.

        Args:
            args: A tuple containing arguments for request_data.

        Returns:
            list or None: A list of dictionaries containing patent data or None if no results are found.
        """
        return self.request_data(*args)

    def run_parallel_requests(self) -> None:
        """Run parallel requests to retrieve patent data and save it to a CSV file."""
        start_size = 0
        num_processes = 20

        with Manager() as manager:
            results_dict = manager.dict()  # Create a shared dictionary for results
            has_results = True

            while has_results:
                # Prepare a list of arguments for request_data
                args_list = [
                    (x, results_dict)
                    for x in range(0, start_size + num_processes * 100, 100)
                ]

                # Call request_data for the current start_size
                # A threadpool would have been a better choice since it would ahve a
                # lower memeory impact.
                with Pool(num_processes) as p:
                    p.map(self.map_request_data, args_list)

                # Check if any of the processes retrieved results
                has_results = any(
                    results_dict.get(start_size, None) is not None
                    for start_size in range(
                        start_size, start_size + num_processes * 100, 100
                    )
                )

                # Increment start_size for the next iteration
                # the * 100 doesn't seem correct. I assume it should be + 100 instead?
                start_size += num_processes * 100

            # Convert the collected results into a DataFrame
            results_list = [
                sublist for sublist in results_dict.values() if sublist is not None
            ]
            result = [x for sublist in results_list for x in sublist]
            df = pd.DataFrame(result)
            # Writing all the data to one file like this is not ideal. If you wanted to
            # say pull all the patents for 2 years, this file would be hundreds of GB in
            # size which would make it impossible to open the file in a python process. It also makes the process of writing to it across different
            # processes challenging.
            output_file_path = os.path.join(output_folder, "export.csv")
            df.to_csv(output_file_path)
            # Why would there be duplicates?
            dup_rows = df[df.duplicated(keep=False)]
            my_logger.info(f"number of duplicated values: {dup_rows}")
            my_logger.info(f"number of data extracted: {len(df)}")
        return result


if __name__ == "__main__":
    # Check the number of command line arguments
    start_date = os.getenv("START_DATE")
    end_date = os.getenv("END_DATE")

    bulk_search = uspto_bulk_search(
        grantFromDate=start_date, grantToDate=end_date, rows=100
    )
    bulk_search.run_parallel_requests()
