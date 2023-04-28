from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired
from wtforms import DecimalField, FileField, SubmitField
from wtforms.validators import InputRequired


class PageForm(FlaskForm):

    number = DecimalField('№ ', validators=[InputRequired()])
    page = FileField('Страница комикса', validators=[FileRequired()])
    submit = SubmitField('Загрузить')

