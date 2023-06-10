import os

from flask import jsonify
from flask_restful import Resource, abort
from werkzeug.security import generate_password_hash

from data import db_session
from ..comment_model import Comment
from ..post_model import Post
from ..theme_model import Theme
from ..user_model import User
from .user_reqparse import parser
from PIL import Image


# Получить пользователя через айди
def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    users = session.query(User).get(user_id)
    if not users:
        abort(404, message=f"User {user_id} not found")


# Сгенерировать хэшированый пароль
def set_password(password):
    return generate_password_hash(password)


# Получить пользователя по айди
class UsersResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        users = session.query(User).get(user_id)
        return jsonify({'user': users.to_dict(only=('name', 'description', 'age', 'number_of_posts',
                                                    'email', 'subscriptions', 'subscribers'))})


# Удалить пользователя (нужен пароль)
class UsersDelete(Resource):
    def delete(self, user_id, password):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        if user.check_password(password):
            for i in user.subscribers.split(','):
                if i != '':
                    sub = session.query(User).get(int(i))
                    list_ = sub.subscriptions.split(',')
                    list_.remove(str(user.id))
                    sub.subscriptions = ','.join(list_)
                    session.commit()
            for i in user.subscriptions.split(','):
                if i != '':
                    sub = session.query(User).get(int(i))
                    list_ = sub.subscribers.split(',')
                    list_.remove(str(user.id))
                    sub.subscribers = ','.join(list_)
                    session.commit()
            posts = session.query(Post).filter(Post.user_id == user.id)
            comments = session.query(Comment).filter(Comment.user_id == user.id)
            session.delete(comments)
            for post in posts:
                os.remove(os.path.abspath(f'static/img/posts/{post.id}.jpg'))
                session.delete(post)
            session.delete(user)
            session.commit()
            os.remove(os.path.abspath(f'static/img/users/{user.id}.jpg'))
            return jsonify({'success': 'OK'})
        return abort(404, message=f"Wrong password, access denied")


# Получить всех пользователей или создать нового
class UsersListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify({'users': [item.to_dict(only=('id', 'name', 'description', 'age', 'number_of_posts',
                                                     'email', 'subscriptions', 'subscribers')) for item in users]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        user = User(
            name=args['name'],
            description=args['description'],
            age=args['age'],
            email=args['email'],
            password=set_password(args['password'])
        )
        user.number_of_posts = 0
        user.subscribers = ''
        user.subscriptions = ''
        for i in args['themes'].split(','):
            if i != '':
                user.themes.append(session.query(Theme).get(int(i)))
        session.add(user)
        session.commit()
        f = Image.open(os.path.abspath('static/img/site/None.png')).convert('L')
        f.save(os.path.abspath(f'static/img/users/{user.id}.jpg'))

        return jsonify({'success': 'OK'})
