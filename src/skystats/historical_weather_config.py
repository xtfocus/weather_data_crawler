# Features at Historical Weather API by Open-meteo

URL = "https://archive-api.open-meteo.com/v1/archive"

HOURLY_COLUMNS = [
    "apparent_temperature",
    "cloud_cover",
    "dew_point_2m",
    "is_day",
    "precipitation",
    "pressure_msl",
    "surface_pressure",
    "temperature_2m",
    "vapour_pressure_deficit",
    "wind_direction_10m",
    "wind_gusts_10m",
    "wind_speed_10m",
]

DAILY_COLUMNS = [
    "apparent_temperature_max",
    "apparent_temperature_min",
    "daylight_duration",
    "precipitation_hours",
    "precipitation_sum",
    "shortwave_radiation_sum",
    "sunrise",
    "sunset",
    "sunshine_duration",
    "temperature_2m_max",
    "temperature_2m_min",
    "weather_code",
    "wind_gusts_10m_max",
    "wind_speed_10m_max",
]


# Hanoi, Vietname
LOCATION = {
    "latitude": 21.0245,
    "longitude": 105.8412,
    "timezone": "Asia/Bangkok",
}
