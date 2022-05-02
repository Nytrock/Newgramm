import sqlalchemy

from data.db_session import SqlAlchemyBase


# Модель тэга в базе данных
class Theme(SqlAlchemyBase):
    __tablename__ = 'theme'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)


# Модель таблицы, связывающей пользователя и тэг
theme_user_table = sqlalchemy.Table(
    'theme_user',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('user', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('user.id')),
    sqlalchemy.Column('theme', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('theme.id'))
)

# Модель таблицы, связывающей пост и тэг
theme_post_table = sqlalchemy.Table(
    'theme_post',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('post', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('post.id')),
    sqlalchemy.Column('theme', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('theme.id'))
)
