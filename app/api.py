import os

import requests
from dotenv import load_dotenv

load_dotenv()


def get_weather(lat: float, lon: float):
    response = requests.get(
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?lat={lat}"
        f"&lon={lon}"
        f"&appid={os.getenv("OPENWEATHERMAP_API_KEY")}"
        f"&units=metric"
    )

    return response.json()
