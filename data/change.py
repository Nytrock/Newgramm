from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import SubmitField, StringField, TextAreaField, SelectMultipleField, FileField, IntegerField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired

from .theme_model import Theme
from . import db_session

db_session.global_init("db/Newgramm.db")


class ChangeForm(FlaskForm):
    name = StringField('Ник', validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[DataRequired()])
    age = IntegerField('Возраст', validators=[DataRequired()])
    email = EmailField('Почта', validators=[DataRequired()])

    db_sess = db_session.create_session()
    result = db_sess.query(Theme).all()
    list_ = []
    for i in result:
        list_.append((str(i.id), i.name))
    themes = SelectMultipleField(u'Какие темы нравятся (для убирания выделения сначала зажмите ctrl)',
                                 choices=list_)
    image = FileField(u'Фото профиля', validators=[FileAllowed(['jpg', 'png'])])

    submit = SubmitField('Ок')
