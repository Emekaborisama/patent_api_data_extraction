"""
This module contains unit tests for the `patent_fetcher` and `custom_logging` modules of the application.

It covers various aspects of the code, including HTTP request mocking, data retrieval, and logging.

Please make sure to run these tests regularly to ensure the correctness of the application's functionality.

The tests are organized as follows:

1. `test_simple`: This function tests the basic functionality of making an HTTP GET request to the API and handling a 404 response using the `responses` library.

2. `uspto_search` fixture: This fixture is used to create an instance of the `uspto_bulk_search` class for testing data retrieval functions.

3. `test_request_data`: This function tests the `request_data` method of the `uspto_bulk_search` class when valid rows are requested.

4. `test_request_data_no_results`: This function tests the `request_data` method of the `uspto_bulk_search` class when no results are returned.

5. `test_request_data_invalid_rows`: This function tests the `request_data` method of the `uspto_bulk_search` class when an invalid number of rows is requested.

6. `test_map_request_data`: This function tests the `map_request_data` method of the `uspto_bulk_search` class.

7. `test_get_logger`: This function tests the `get_logger` function from the `custom_logging` module.

Make sure to maintain and update these tests as the application evolves to catch any regressions and ensure code quality.
"""

import logging
import os

import pandas as pd
import pytest
import requests
import responses
from app import custom_logging, patent_fetcher


@responses.activate
def test_simple():
    # register via direct arguments
    responses.add(
        responses.GET,
        patent_fetcher.API_URL,
        json={"error": "not found"},
        status=404,
    )

    resp = requests.get(patent_fetcher.API_URL)
    print(resp.status_code)
    assert resp.json() == {"error": "not found"}
    assert resp.status_code == 404


@pytest.fixture
def uspto_search():
    return patent_fetcher.uspto_bulk_search("2001-01-01", "2022-01-31", 10)


def test_request_data(uspto_search):
    results_dict = {}
    uspto_search.request_data(0, results_dict)
    assert len(results_dict) == 1
    assert len(results_dict[0]) == 10


def test_request_data_no_results(uspto_search):
    results_dict = {}
    uspto_search.request_data(10, results_dict)
    assert len(results_dict) == 1


def test_request_data_invalid_rows(uspto_search):
    results_dict = {}
    uspto_search.request_data(-10, results_dict)
    print(uspto_search.request_data(-10, results_dict))
    assert len(results_dict) == 0


def test_map_request_data():
    uspto_search = patent_fetcher.uspto_bulk_search("2001-01-01", "2022-01-31", 10)
    result = uspto_search.map_request_data((0, {}))
    assert result == None


def test_get_logger():
    logger = custom_logging.get_logger("test_logger")
    assert isinstance(logger, logging.Logger)
