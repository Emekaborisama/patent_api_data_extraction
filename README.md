# Patent_api_extraction
speed up X2 api request data extraction (uspto patent DB) using python curl



## Code Explanation
Here's an overview of the logic and structure of the code:

- Initializes the USPTO Bulk Search object with date range and row count.

- request_data: Makes requests to the USPTO API and retrieves patent data. It supports parallel processing and recursively retries in case of API rate limits.

- map_request_data: A mapping function used for parallel processing of request_data.

- run_parallel_requests: Runs parallel requests to retrieve patent data and saves it to a CSV file.


## How to Run


- git clone


- Build docker image 
```bash

docker build -t patent_fetcher .
```

- run patent_fetcher  with start and end date

```bash 

docker run -e START_DATE=2001-01-01 -e END_DATE=2012-01-03 patent_fetcher
```

- if you want to export your csv use the command below

```bash 
docker run -v $(pwd):/app/data -e START_DATE=2001-01-01 -e END_DATE=2012-01-03 patent_fetcher
```

# How to run test

```bash 

python3 -m pytest test.py
```




## Future Test

- Logging Tests:
Test that log messages are generated correctly, especially error messages.

- Concurrency and Parallelism Tests:

Test the behavior of your code under different levels of concurrency (e.g., varying the number of processes in run_parallel_requests).

- Exception Handling Tests:
Tests to ensure that exceptions are correctly raised and handled in your code. 

- More API Error Handling Tests:

Test how your code handles different API error scenarios, such as 400 Bad Request, 401 Unauthorized, and 500 Internal Server Error. Ensure that the error responses are correctly processed and logged.

- Retry Mechanism Tests:
Test the behavior of your retry mechanism when it encounters errors. Verify that it retries the request according to your specified retry logic.
