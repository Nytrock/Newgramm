from wtforms import Form, SelectField, SubmitField


class SortForm(Form):
    sorting = SelectField(u'Сортировка по:', coerce=int)
    submit = SubmitField('Сортировать')
