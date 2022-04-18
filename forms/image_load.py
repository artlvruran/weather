from wtforms import FileField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired


class ImageForm(FlaskForm):
    image = FileField('image', validators=[DataRequired()])