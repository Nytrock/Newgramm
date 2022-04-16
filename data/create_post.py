import os

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import SubmitField, TextAreaField, FileField, SelectMultipleField, validators, BooleanField
from wtforms.validators import DataRequired
from . import db_session
from .theme_model import Theme

file_path = os.path.join(os.path.abspath('../'), 'db', 'NewGramm.db')
db_session.global_init(file_path)


class PostForm(FlaskForm):
    description = TextAreaField('Описание поста', validators=[DataRequired(), validators.Length(min=4, max=500)])
    image = FileField(u'Фотография', validators=[FileAllowed(['jpg', 'png'])])
    comments = BooleanField('Коментарии включены', default=True)

    db_sess = db_session.create_session()
    result = db_sess.query(Theme).all()
    list_ = []
    for i in result:
        list_.append((str(i.id), i.name))
    themes = SelectMultipleField(u'Темы поста (для выбора нескольких вариантов или убирания одного зажмите ctrl)',
                                 choices=list_)

    submit = SubmitField('Ок')
