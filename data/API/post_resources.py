import datetime
import os

from PIL import Image
from flask import jsonify
from flask_restful import Resource, abort

from data import db_session
from ..theme_model import Theme
from ..user_model import User
from ..post_model import Post
from ..comment_model import Comment
from .post_reqparse import parser


# Найти пост по айди
def abort_if_post_not_found(post_id):
    session = db_session.create_session()
    posts = session.query(Post).get(post_id)
    if not posts:
        abort(404, message=f"Post {post_id} not found")


# Получить один пост
class PostsResource(Resource):
    def get(self, post_id):
        abort_if_post_not_found(post_id)
        session = db_session.create_session()
        posts = session.query(Post).get(post_id)
        return jsonify({'post': posts.to_dict(only=('user_id', 'description', 'likes', 'publication_date',
                                                     'themes'))})


# Удалить пост (нужен пароль)
class PostsDelete(Resource):
    def delete(self, post_id, password):
        abort_if_post_not_found(post_id)
        session = db_session.create_session()
        post = session.query(Post).get(post_id)
        user = session.query(User).get(post.user_id)
        user.number_of_posts -= 1
        if user.check_password(password):
            session.delete(post)
            os.remove(os.path.abspath(f'static/img/posts/{post.id}.jpg'))
            comments = session.query(Comment).filter(Comment.post_id == post.id)
            session.delete(comments)
            session.commit()
            return jsonify({'success': 'OK'})
        return abort(404, message=f"Wrong password, access denied")


# Получить все посты или создать новый (нужен пароль)
class PostsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        posts = session.query(Post).all()
        return jsonify({'posts': [item.to_dict(only=('id', 'user_id', 'description', 'likes', 'publication_date',
                                                     'themes')) for item in posts]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        user = session.query(User).get(args["user_id"])
        if user:
            if user.check_password(args["password"]):
                post = Post(
                    user_id=args['user_id'],
                    description=args['description']
                )
                post.publication_date = datetime.datetime.now()
                post.likes = ''
                for i in args['themes'].split(','):
                    if i != '':
                        post.themes.append(session.query(Theme).get(int(i)))
                user.number_of_posts += 1
                session.add(post)
                session.commit()
                f = Image.open(os.path.abspath('static/img/site/None.png')).convert('L')
                f.save(os.path.abspath(f'static/img/posts/{post.id}.jpg'))
                return jsonify({'success': 'OK'})
            return abort(404, message=f"Wrong password, access denied")
        return abort(404, message=f"Wrong user id")
