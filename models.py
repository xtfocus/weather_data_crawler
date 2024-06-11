import re

from pydantic import BaseModel, field_validator


class WeatherData(BaseModel):
    pressure: str
    humidity: str
    temperature: str
    weather_summary: str
    wind_power: str
    wind_dir: str

    @field_validator("pressure")
    def validate_pressure(cls, value):
        pattern = r"^\d{3,4} mbar$"
        if not re.match(pattern, value):
            raise ValueError(f"Invalid pressure format: {value}")
        return value

    @field_validator("humidity")
    def validate_humidity(cls, value):
        pattern = r"^\d{1,3}%$"
        if not re.match(pattern, value):
            raise ValueError(f"Invalid humidity format: {value}")
        return value

    @field_validator("temperature")
    def validate_temperature(cls, value):
        pattern = r"^\d{1,2}°C$"
        if not re.match(pattern, value):
            raise ValueError(f"Invalid temperature format: {value}")
        return value

    @field_validator("wind_power")
    def validate_wind_power(cls, value):
        pattern = r"^\d{1,2} km/h$"
        if not re.match(pattern, value):
            raise ValueError(f"Invalid wind power format: {value}")
        return value

    @field_validator("wind_dir")
    def validate_data(cls, value):
        if not value or not isinstance(value, str):
            raise ValueError("Invalid wind direction")
        return value


class AirData(BaseModel):
    aqi_value: str
    aqi_status_text: str
    recommendation_detail: str

    @field_validator("aqi_value")
    def validate_aqi_value(cls, value):
        pattern = r"^\d{1,3}$"
        if not re.match(pattern, value):
            raise ValueError(f"Invalid AQI value format: {value}")
        return value

    @field_validator("aqi_status_text")
    def validate_aqi_status_text(cls, value):
        allowed_values = [
            "Good",
            "Moderate",
            "Unhealthy for Sensitive Groups",
            "Unhealthy",
            "Very Unhealthy",
            "Hazardous",
        ]
        if value not in allowed_values:
            raise ValueError(f"Invalid AQI status text: {value}")
        return value

    @field_validator("recommendation_detail")
    def validate_recommendation_detail(cls, value):
        if not value:
            raise ValueError("Recommendation detail cannot be empty")
        return value
