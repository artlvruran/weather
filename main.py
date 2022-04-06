import os
import sys
import requests

from flask import Flask, render_template, request
from constants import *


def celc_from_kelvin(temp):
    return round(temp - 273.15)


app = Flask(__name__)


@app.route("/weather/<city>")
def general(city):
    geocoder_req = f"https://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={city}&format=json"
    response = requests.get(geocoder_req).json()
    pos = response['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos'].split()

    current_weather_request = f'https://api.openweathermap.org/data/2.5/weather?lat={pos[1]}&lon={pos[0]}&lang=en&appid={WEATHER_API_KEY}'
    weather_response = requests.get(current_weather_request).json()

    params = {
        "city": weather_response["name"] if weather_response["name"] else city,
        "temperature": f'{celc_from_kelvin(weather_response["main"]["temp"])} °C',
        "icon": f'https://openweathermap.org/img/wn/{weather_response["weather"][0]["icon"]}.png'
    }

    return render_template('general.html', **params)


"""@app.route("/login")
def login():


@app.route("/sign_up")
def signup():


@app.route("/news")
def news():
"""

if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')