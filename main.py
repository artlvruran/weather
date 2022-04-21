import os

import sqlalchemy
from flask import Flask, render_template, redirect
from constants import *
from forms.user import RegisterForm, LoginForm
from forms.image_load import ImageForm
from data import db_session
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from data.users import User
from data import weather, map_page
from flask_uploads import UploadSet, IMAGES, configure_uploads
import logging


db_session.global_init("db/users.db")
app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['UPLOADED_PHOTOS_DEST'] = UPLOAD_FOLDER
app.register_blueprint(weather.blueprint)
app.register_blueprint(map_page.blueprint)
images = UploadSet('photos', IMAGES)
configure_uploads(app, images)
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
            city=form.city.data,
            avatar_image=sqlalchemy.null()
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Registration', form=form)


@app.route('/', methods=['GET', 'POST'])
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


@app.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    form = ImageForm()
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.name == username).first()
    if user.name == current_user.name:
        if form.validate_on_submit():
            filename = images.save(form.image.data)
            user.avatar_image = filename
            db_sess.commit()
        params = {
            'user': user,
            'form': form
        }
        logging.warning(f'user: {current_user.name}')
        return render_template('user.html', **params)
    else:
        return 'Access denied'


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
