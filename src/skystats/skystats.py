import argparse
from datetime import date, datetime
from typing import Any

import openmeteo_requests
import pandas as pd
import requests_cache
from loguru import logger
from pydantic import BaseModel, Field, ValidationInfo, field_validator
from retry_requests import retry

from .historical_weather_config import DAILY_COLUMNS, HOURLY_COLUMNS, LOCATION, URL
from .models import DateModel


def setup_openmeteo_client() -> openmeteo_requests.Client:
    """
    Setup the Open-Meteo API client with cache and retry on error.

    Returns:
        openmeteo_requests.Client: An instance of the Open-Meteo client.
    """
    cache_session = requests_cache.CachedSession(".cache", expire_after=-1)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)
    return openmeteo


def get_historical_hourly_data(
    openmeteo: openmeteo_requests.Client, date_range: DateModel
) -> pd.DataFrame:
    """
    Retrieve historical hourly weather data for a specified date range.

    Args:
        openmeteo (openmeteo_requests.Client): The Open-Meteo API client.
        start_date (str): The start date of the data range in "YYYY-MM-DD" format.
        end_date (str): The end date of the data range in "YYYY-MM-DD" format.

    Returns:
        pd.DataFrame: A DataFrame containing the historical hourly weather data.
    """

    params = {
        **LOCATION,
        "start_date": str(date_range.start_date),
        "end_date": str(date_range.end_date),
        "hourly": HOURLY_COLUMNS,
    }

    responses = openmeteo.weather_api(URL, params=params)

    response = responses[0]
    logger.info(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
    logger.info(f"Elevation {response.Elevation()} m asl")
    logger.info(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
    logger.info(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

    hourly = response.Hourly()
    hourly_data = {
        "date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left",
        )
    }

    for i, col in enumerate(HOURLY_COLUMNS):
        hourly_data[col] = hourly.Variables(i).ValuesAsNumpy()

    hourly_dataframe = pd.DataFrame(data=hourly_data)
    logger.info("Hourly data retrieved successfully")
    return hourly_dataframe


def get_historical_daily_data(
    openmeteo: openmeteo_requests.Client, date_range: DateModel
) -> pd.DataFrame:
    """
    Retrieve historical daily weather data for a specified date range.

    Args:
        openmeteo (openmeteo_requests.Client): The Open-Meteo API client.
        start_date (str): The start date of the data range in "YYYY-MM-DD" format.
        end_date (str): The end date of the data range in "YYYY-MM-DD" format.

    Returns:
        pd.DataFrame: A DataFrame containing the historical daily weather data.
    """

    params = {
        **LOCATION,
        "daily": DAILY_COLUMNS,
        "start_date": str(date_range.start_date),
        "end_date": str(date_range.end_date),
    }

    responses = openmeteo.weather_api(URL, params=params)

    response = responses[0]
    logger.info(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
    logger.info(f"Elevation {response.Elevation()} m asl")
    logger.info(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
    logger.info(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

    daily = response.Daily()
    daily_data = {
        "date": pd.date_range(
            start=pd.to_datetime(daily.Time(), unit="s", utc=True),
            end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=daily.Interval()),
            inclusive="left",
        )
    }

    for i, col in enumerate(DAILY_COLUMNS):
        daily_data[col] = daily.Variables(i).ValuesAsNumpy()

    daily_dataframe = pd.DataFrame(data=daily_data)
    logger.info("Daily data retrieved successfully")
    return daily_dataframe


def get_history_weather(start_date: str, end_date: str, frequency: str):
    """
    Validate date inputs and execute GET
    """
    openmeteo = setup_openmeteo_client()

    date_range = DateModel(
        start_date=datetime.strptime(start_date, "%Y-%m-%d").date(),
        end_date=datetime.strptime(end_date, "%Y-%m-%d").date(),
    )

    if frequency == "hourly":
        data = get_historical_hourly_data(openmeteo, date_range)
    elif frequency == "daily":
        data = get_historical_daily_data(openmeteo, date_range)
    else:
        raise ValueError("Invalid data type. Choose 'hourly' or 'daily'.")

    logger.info(data.head())
    return data


def cli():
    parser = argparse.ArgumentParser(
        prog="skystats", description="Fetch historical weather data."
    )

    # Specify all args as mandatory and explicit (like python mandatory kwarg) with required=True + shorthands
    parser.add_argument(
        "-s",
        "--start-date",
        required=True,
        type=str,
        help="Start date in the format YYYY-MM-DD",
    )
    parser.add_argument(
        "-e",
        "--end-date",
        required=True,
        type=str,
        help="End date in the format YYYY-MM-DD",
    )
    parser.add_argument(
        "-f",
        "--frequency",
        type=str,
        choices=["hourly", "daily"],
        required=True,
        help="Frequency of data to fetch: hourly or daily",
        default="daily",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        required=False,
        help="Name of output parquet file",
    )

    args = parser.parse_args()

    data = get_history_weather(
        args.start_date, args.end_date, args.frequency
    )  # argparse understand --start-date is start_date

    if args.output:
        output_file = f"{args.output}.parquet"
        data.to_parquet(output_file)
        logger.success(f"Historical data saved to {output_file}. Lines: {len(data)}")


if __name__ == "__main__":
    cli()
