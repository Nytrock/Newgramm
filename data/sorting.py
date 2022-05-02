from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField


# Форма для сортировки
class SortForm(FlaskForm):
    sorting = SelectField(u'Сортировка по:', coerce=int)
    submit = SubmitField('Сортировать')
