from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import SubmitField, TextAreaField, FileField, SelectMultipleField
from wtforms.validators import DataRequired
from . import db_session
from .theme_model import Theme

db_session.global_init("db/Newgramm.db")


class PostForm(FlaskForm):
    description = TextAreaField('Описание поста', validators=[DataRequired()])
    image = FileField(u'Фотография', validators=[FileAllowed(['jpg', 'png'])])

    db_sess = db_session.create_session()
    result = db_sess.query(Theme).all()
    list_ = []
    for i in result:
        list_.append((str(i.id), i.name))
    themes = SelectMultipleField(u'Темы поста (для убирания выделения сначала зажмите ctrl)',
                                 choices=list_)

    submit = SubmitField('Ок')
