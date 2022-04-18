from wtforms import FileField
from flask_wtf import FlaskForm


class ImageForm(FlaskForm):
    image = FileField('image')