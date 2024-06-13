# skystats

Simple weather data crawler from some weather apps/websites.

Air quality: https://www.iqair.com/vietnam/hanoi

Live weather: https://timeanddate.com/weather/vietnam/hanoi

Historical data: https://open-meteo.com

## Install

```bash
pip install git+https://github.com/xtfocus/weather_data_crawler.git
```

## Usage

#### Live Weather
```bash
skynow
```

Example output:

```
2024-06-11 15:33:19.471 | INFO     | __main__:main:144 - Query time = 2024-06-11 15:33
2024-06-11 15:33:19.471 | SUCCESS  | __main__:main:145 - Air Data: aqi_value='67' aqi_status_text='Moderate' recommendation_detail='Sensitive groups should reduce outdoor exercise\nClose your windows to avoid dirty outdoor air\nSensitive groups should wear a mask outdoors\nSensitive groups should run an air purifier'
2024-06-11 15:33:19.478 | SUCCESS  | __main__:main:155 - Weather Data: pressure='1003 mbar' humidity='60%' temperature='35°C' weather_summary='Passing clouds.' wind_power='17 km/h' wind_dir='Wind blowing from 130° Southeast to Northwest'
```

#### Weather History

Get daily weather stats from 2022 Jan 1st till 2022 Feb 1st:
```bash
skystats -s 2022-01-01 -e 2022-02-01 -f daily # options: daily, hourly
```
