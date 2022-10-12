import requests
import json

def get_weather():
    URL_WEATHER = 'https://api.openweathermap.org/data/2.5/weather?lat=45.8131&lon=15.9775&appid=c163b84baf8d18224d033965b14128af&units=metric&lang=hr'
    weather_response = requests.get(URL_WEATHER)
    return json.loads(weather_response.text)
