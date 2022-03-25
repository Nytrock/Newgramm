import datetime

import sqlalchemy
from sqlalchemy import orm

from data.db_session import SqlAlchemyBase


class Post(SqlAlchemyBase):
    __tablename__ = 'post'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("user.id"))
    picture = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    publication_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    likes = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, default=0)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    themes = orm.relation("Theme",
                          secondary="theme_post",
                          backref="post")
