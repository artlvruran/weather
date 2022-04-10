import logging
import os
import sys
import requests
import datetime

from flask import Flask, render_template, request, redirect
from constants import *
from forms.user import RegisterForm, LoginForm
from data import db_session
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from data.users import User


def celc_from_kelvin(temp):
    return round(temp - 273.15)


db_session.global_init("db/users.db")
app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/weather/<city>")
@login_required
def general(city):
    geocoder_req = f"https://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={city}&format=json"
    response = requests.get(geocoder_req).json()
    pos = response['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos'].split()

    # Текущая погода
    current_weather_request = f'https://api.openweathermap.org/data/2.5/weather?lat={pos[1]}&lon={pos[0]}&lang=en&appid={WEATHER_API_KEY}'
    weather_response = requests.get(current_weather_request).json()

    # Прогноз
    forecast_request = f'https://api.openweathermap.org/data/2.5/onecall?lat={pos[1]}&lon={pos[0]}&appid={WEATHER_API_KEY}'
    forecast = requests.get(forecast_request).json()

    forecast_hourly = [{
                        "time": datetime.datetime.utcfromtimestamp(int(forecast["hourly"][i]["dt"]) + int(forecast["timezone_offset"])).strftime('%H:%M'),
                        "temp": f'{celc_from_kelvin(forecast["hourly"][i]["temp"])} °C',
                        "icon": f'https://openweathermap.org/img/wn/{forecast["hourly"][i]["weather"][0]["icon"]}.png'
                        }
                       for i in range(len(forecast["hourly"]))]

    forecast_daily = [{
                        "time": datetime.datetime.utcfromtimestamp(int(forecast["daily"][i]["dt"]) + int(forecast["timezone_offset"])).strftime('%d.%m'),
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

    return render_template('general.html', **params)


@app.route("/logout")
def logout():
    logout_user()
    return redirect('/weather/Moscow')


@app.route("/register", methods=['POST', 'GET'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Registration',
                                   form=form,
                                   message="Passwords does not match")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Registration',
                                   form=form,
                                   message="This user is already exist")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data,
            city=form.city.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Registration', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect(f"/weather/{user.city}")
        return render_template('login.html',
                               message="Incorrect login or password",
                               form=form)
    return render_template('login.html', title='Logging in', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.name == username).first()
    params = {
        'user': user
    }
    return render_template('user.html', **params)


"""@app.route("/news")
def news():
"""

if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
