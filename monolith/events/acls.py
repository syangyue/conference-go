import requests
from .keys import PEXELS_API_KEY, OPEN_WEATHER_API_KEY
import json


def get_weather_data(city, state):
    """"
    weather": {
    "temp": temperature in Fahrenheit (imperial measure),
    "description": the description of the weather, like "overcast clouds"
     },

    """
    url = "http://api.openweathermap.org/geo/1.0/direct"
    params = {
        "q": f"{city}, {state}, 'US'",
        "appid": OPEN_WEATHER_API_KEY,

    }
    response = requests.get(url, params=params)
    content = json.loads(response.content)
    latitude = content[0]["lat"]
    longitude = content[0]["lon"]
    url2 = "https://api.openweathermap.org/data/2.5/weather"
    params2 = {
        "lat": latitude,
        "lon": longitude,
        "appid": OPEN_WEATHER_API_KEY,
        "units": "imperial"
    }
    response2 = requests.get(url2, params=params2)
    content2 = json.loads(response2.content)
    weather = {
            "temp": int(content2["main"]["temp"]),
            "description": content2["weather"][0]["description"]
        }

    return weather


def get_photo(city, state):
    headers = {"Authorization": PEXELS_API_KEY}
    parameters = {
        "per_page": 1,
        "query": city + " " + state
    }
    url = "https://api.pexels.com/v1/search"
    response = requests.get(url, params=parameters, headers=headers)
    content = json.loads(response.content)

    try:
        return {"picture_url": content["photos"][0]["src"]["original"]}
    except Exception:
        return {"picture_url": None}
