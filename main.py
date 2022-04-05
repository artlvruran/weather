import os
import sys
import requests

from flask import Flask, render_template, request
from constants import *

app = Flask(__name__)


@app.route("/weather/<city>")
def general(city):
    geocoder_req = f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={city}&format=json"
    response = requests.get(geocoder_req).json()
    pos = response['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos'].split()

    current_weather_request = f'https://api.openweathermap.org/data/2.5/weather?lat={pos[1]}&lon={pos[0]}&appid={WEATHER_API_KEY}'
    weather_response = requests.get(current_weather_request).json()

    return weather_response

    return render_template('main.html')


"""@app.route("/login")
def login():


@app.route("/sign_up")
def signup():


@app.route("/news")
def news():
"""

if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')