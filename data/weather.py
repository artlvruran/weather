import logging

import flask
import requests
import datetime
from constants import *
from flask import render_template, request, redirect, url_for
from flask_login import login_required


def celc_from_kelvin(temp):
    return round(temp - 273.15)


blueprint = flask.Blueprint(
    'weather',
    __name__,
    template_folder='templates'
)


@blueprint.route("/weather/<city>")
@login_required
def get_weather(city):
    geocoder_req = f"https://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={city}&format=json"
    response = requests.get(geocoder_req).json()
    pos = response['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos'].split()

    # Текущая погода
    current_weather_request = f'https://api.openweathermap.org/data/2.5/weather?lat={pos[1]}&lon={pos[0]}&lang=en&appid={WEATHER_API_KEY}'
    weather_response = requests.get(current_weather_request).json()
    logging.warning(current_weather_request)
    # Прогноз
    forecast_request = f'https://api.openweathermap.org/data/2.5/onecall?lat={pos[1]}&lon={pos[0]}&appid={WEATHER_API_KEY}'
    forecast = requests.get(forecast_request).json()

    forecast_hourly = [{
        "time": datetime.datetime.utcfromtimestamp(
            int(forecast["hourly"][i]["dt"]) + int(forecast["timezone_offset"])).strftime('%H:%M'),
        "temp": f'{celc_from_kelvin(forecast["hourly"][i]["temp"])} °C',
        "icon": f'https://openweathermap.org/img/wn/{forecast["hourly"][i]["weather"][0]["icon"]}.png'
    }
        for i in range(len(forecast["hourly"]))]

    forecast_daily = [{
        "time": datetime.datetime.utcfromtimestamp(
            int(forecast["daily"][i]["dt"]) + int(forecast["timezone_offset"])).strftime('%d.%m'),
        "temp_day": f'{celc_from_kelvin(forecast["daily"][i]["temp"]["day"])} °C',
        "temp_night": f'{celc_from_kelvin(forecast["daily"][i]["temp"]["night"])} °C',
        "icon": f'https://openweathermap.org/img/wn/{forecast["daily"][i]["weather"][0]["icon"]}.png'
    }
        for i in range(len(forecast["daily"]))]

    params = {
        "city": weather_response["name"] if weather_response["name"] else city,
        "temperature": f'{celc_from_kelvin(weather_response["main"]["temp"])} °C',
        "icon": f'https://openweathermap.org/img/wn/{weather_response["weather"][0]["icon"]}.png',
        "main": weather_response['weather'][0]['description'],
        "max": f"{celc_from_kelvin(weather_response['main']['temp_max'])} °C",
        "min": f"{celc_from_kelvin(weather_response['main']['temp_min'])} °C",
        "forecast_hourly": forecast_hourly,
        "forecast_daily": forecast_daily,
        "feels_like": f'{celc_from_kelvin(weather_response["main"]["feels_like"])} °C',
        "pressure": f'{round(0.750064 * float(weather_response["main"]["pressure"]), 1)} Hg',
        "wind_speed": f'{weather_response["wind"]["speed"]} m/s'
    }

    request = f'https://serpapi.com/search?engine=yandex_images&text={params["city"]}&api_key={SERPAPI_API_KEY}'
    image_response = requests.get(request).json()
    try:
        params["image"] = image_response["images_results"][0]["original"]
    except IndexError:
        try:
            request = f'https://serpapi.com/search?engine=yandex_images&text={city}&api_key={SERPAPI_API_KEY}'
            image_response = requests.get(request).json()
            params["image"] = image_response["hits"][0]['largeImageURL']
        except IndexError:
            params["image"] = BASE_CITY_IMAGE

    return render_template('general.html', **params)


@blueprint.route('/weather/<city>', methods=['POST'])
def get_city(city):
    text = request.form['search']
    return redirect(f'/weather/{text}')
