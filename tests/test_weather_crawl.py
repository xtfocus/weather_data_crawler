# tests/test_aqi_extractor.py
import pytest
from bs4 import BeautifulSoup
from loguru import logger

from app import extract_aqi_data, extract_weather_data


@pytest.fixture
def mocked_aqi_response():
    with open("tests/mocked_aqi_page.html", "r") as f:
        return f.read()


@pytest.fixture
def mocked_weather_response():
    with open("tests/mocked_weather_page.html", "r") as f:
        return f.read()


def test_extract_aqi_data(mocked_aqi_response):
    soup = BeautifulSoup(mocked_aqi_response, "html.parser")

    aqi_value, aqi_status_text, recommendation_detail = extract_aqi_data(soup)

    assert int(aqi_value) == 75
    assert aqi_status_text == "Moderate"
    assert "Sensitive groups" in recommendation_detail


def test_extract_weather_data(mocked_weather_response):
    soup = BeautifulSoup(mocked_weather_response, "html.parser")

    (
        pressure,
        humidity,
        temperature,
        summary,
        wind_power,
        wind_dir,
    ) = extract_weather_data(soup)

    assert pressure == "1005 mbar"
    assert humidity == "67%"
    assert temperature == "34°C"
    assert summary == "Partly sunny."
    assert wind_power == "11 km/h"
    assert wind_dir == "Wind blowing from 0° North to South"
