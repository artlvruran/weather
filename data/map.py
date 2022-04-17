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
    'map',
    __name__,
    template_folder='templates'
)


@blueprint.route('/map/<lon>/<lat>')
@login_required
def get_map(lon, lat):
    params = {
        'lat': lat,
        'lon': lon
    }
    return render_template('map.html', **params)


@blueprint.route('/map/<city>')
@login_required
def get_map_by_city(city):
    geocoder_req = f"https://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={city}&format=json"
    logging.warning('getting city')
    response = requests.get(geocoder_req).json()
    pos = response['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos'].split()
    params = {
        'lon': pos[0],
        'lat': pos[1]
    }
    return redirect(url_for('map.get_map', **params))