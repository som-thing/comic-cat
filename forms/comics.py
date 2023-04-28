from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired
from wtforms import StringField, TextAreaField, FileField, SubmitField, SelectField
from wtforms.validators import DataRequired, InputRequired


class ComicsForm(FlaskForm):

    name = StringField('Название комикса', validators=[DataRequired()])
    about = TextAreaField("Описание комикса")
    cover = FileField('Обложка комикса', validators=[FileRequired()])
    genres = SelectField('Жанр', coerce=int, validators=[InputRequired()])
    submit = SubmitField('Загрузить')

