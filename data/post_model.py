import datetime

import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from data.db_session import SqlAlchemyBase


# Модель поста в базе данных
class Post(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'post'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("user.id"))
    publication_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    likes = sqlalchemy.Column(sqlalchemy.String, nullable=False, default=0)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    enable_comments = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
    themes = orm.relation("Theme",
                          secondary="theme_post",
                          backref="post")
