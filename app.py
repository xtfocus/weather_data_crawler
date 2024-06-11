import json
import os
from datetime import datetime
from typing import Optional, Tuple

import requests
from bs4 import BeautifulSoup, Tag
from dotenv import load_dotenv
from loguru import logger

from models import AirData, WeatherData

load_dotenv(".env_dev")

AIR_URL = os.environ["AIR_URL"]
WEATHER_URL = os.environ["WEATHER_URL"]


def get_soup(url: str) -> Optional[BeautifulSoup]:
    """
    Sends a GET request to the given URL and returns a BeautifulSoup object if the response is successful.

    Args:
        url (str): The URL to request.

    Returns:
        Optional[BeautifulSoup]: A BeautifulSoup object containing the parsed HTML content, or None if the request failed.
    """
    response = requests.get(url)
    if response.status_code == 200:
        return BeautifulSoup(response.content, "html.parser")
    return None


def extract_weather_data(soup: BeautifulSoup) -> Tuple[str, str, str, str, str, str]:
    """
    Extracts weather data from the provided BeautifulSoup object.

    Args:
        soup (BeautifulSoup): A BeautifulSoup object containing the HTML content.

    Returns:
        Tuple[str, str, str, str, str, str]: A tuple containing pressure, humidity, temperature, summary, wind power, and wind direction.
    """
    info_1 = [i.text.strip() for i in soup.select("div.bk-focus__info td")][:-1]

    pressure = info_1[4]
    humidity = info_1[-1]
    info_2 = soup.select_one("div.bk-focus__qlook")
    temperature = info_2.select_one("div.h2").text.replace("\xa0", "")
    wind_dir = info_2.select_one('span[class^="comp"]').get("title")

    summary = info_2.select_one("p").text
    wind_power = list(info_2.find_all("p")[-1].strings)[2].split(":")[1].strip()

    return (pressure, humidity, temperature, summary, wind_power, wind_dir)


def soup_to_weather_data(soup: BeautifulSoup) -> WeatherData:
    """
    Converts a BeautifulSoup object to a WeatherData object.

    Args:
        soup (BeautifulSoup): A BeautifulSoup object containing the HTML content.

    Returns:
        WeatherData: An object containing the weather data.
    """
    (
        pressure,
        humidity,
        temperature,
        summary,
        wind_power,
        wind_dir,
    ) = extract_weather_data(soup)

    return WeatherData(
        pressure=pressure,
        humidity=humidity,
        temperature=temperature,
        weather_summary=summary,
        wind_power=wind_power,
        wind_dir=wind_dir,
    )


def extract_aqi_data(soup: BeautifulSoup) -> Tuple[str, str, str]:
    """
    Extracts AQI data from the provided BeautifulSoup object.

    Args:
        soup (BeautifulSoup): A BeautifulSoup object containing the HTML content.

    Returns:
        Tuple[str, str, str]: A tuple containing AQI value, AQI status text, and recommendation details.
    """

    aqi_status_summary = soup.find("div", {"class": "aqi-overview__summary aqi-yellow"})
    aqi_status_text = aqi_status_summary.find(attrs={"class": "aqi-status__text"}).text
    aqi_value = aqi_status_summary.find(attrs={"class": "aqi-value__value"}).text

    recommendations = soup.find("div", {"class": "recommendation__detail"})
    # Remove commercial links
    product_links = recommendations.find_all("a")
    [product_link.decompose() for product_link in product_links]
    recommendation_detail = [i.text.strip() for i in recommendations.find_all("tr")]
    recommendation_detail = "\n".join(recommendation_detail)

    return aqi_value, aqi_status_text, recommendation_detail


def soup_to_air_data(soup: BeautifulSoup) -> AirData:
    """
    Converts a BeautifulSoup object to an AirData object.

    Args:
        soup (BeautifulSoup): A BeautifulSoup object containing the HTML content.

    Returns:
        AirData: An object containing the AQI data.
    """
    aqi_value, aqi_status_text, recommendation_detail = extract_aqi_data(soup)

    return AirData(
        aqi_value=aqi_value,
        aqi_status_text=aqi_status_text,
        recommendation_detail=recommendation_detail,
    )


def main():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    air_soup = get_soup(AIR_URL)
    weather_soup = get_soup(WEATHER_URL)

    result = dict()

    if not air_soup:
        logger.exception("Error requesting aqi information")
    else:
        try:
            air_data = soup_to_air_data(air_soup)
            logger.info(f"Query time = {now}")
            logger.success(f"Air Data: {air_data}")
            result["air_data"] = dict(air_data)
        except ValueError as e:
            logger.exception(f"Error parsing aqi information: {e}")

    if not weather_soup:
        logger.exception("Error requesting weather information")
    else:
        try:
            weather_data = soup_to_weather_data(weather_soup)
            logger.success(f"Weather Data: {weather_data}")
            result["weather_data"] = dict(weather_data)
        except ValueError as e:
            logger.exception(f"Error parsing weather information: {e}")

    if result:
        return json.dumps(result)


if __name__ == "__main__":
    json_string = main()
