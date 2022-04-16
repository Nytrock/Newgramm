import os

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import SubmitField, StringField, PasswordField, TextAreaField, SelectMultipleField, FileField, \
    IntegerField, validators
from wtforms.fields import EmailField
from wtforms.validators import DataRequired
from .theme_model import Theme
from . import db_session

file_path = os.path.join(os.path.abspath('.'), 'db', 'NewGramm.db')
db_session.global_init(file_path)


class RegisterForm(FlaskForm):
    name = StringField('Ник', validators=[DataRequired(), validators.Length(min=4, max=22)])
    description = TextAreaField('Описание', validators=[DataRequired(), validators.Length(min=4, max=100)])
    age = IntegerField('Возраст', validators=[DataRequired(), validators.NumberRange(min=1, max=100)])
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    image = FileField(u'Фото профиля', validators=[FileAllowed(['jpg', 'png'])])

    db_sess = db_session.create_session()
    result = db_sess.query(Theme).all()
    list_ = []
    for i in result:
        list_.append((str(i.id), i.name))
    list_.sort()
    themes = SelectMultipleField(u'Какие темы нравятся (для выбора нескольких вариантов или убирания одного зажмите ctrl)',
                                 choices=list_)

    submit = SubmitField('Ок')
