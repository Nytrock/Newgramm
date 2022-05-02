from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, validators, StringField
from wtforms.validators import DataRequired


# Форма поиска
class SearchForm(FlaskForm):
    types = SelectField(u'Искать  по', coerce=int)
    name = StringField('Имя', validators=[DataRequired(), validators.Length(max=22)])
    submit = SubmitField('Поиск')
