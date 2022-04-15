import logging
import os
import sys

import flask_login
import requests
import datetime

from flask import Flask, render_template, request, redirect
from constants import *
from forms.user import RegisterForm, LoginForm
from data import db_session
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from data.users import User
from data import weather
import logging


db_session.global_init("db/users.db")
app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.register_blueprint(weather.blueprint)
logging.basicConfig(filename='example.log')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


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
    if user.name == flask_login.current_user.name:
        params = {
            'user': user
        }
        logging.warning(f'user: {flask_login.current_user.name}')
        return render_template('user.html', **params)
    else:
        return 'Access denied'


"""@app.route("/news")
def news():
"""

if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
