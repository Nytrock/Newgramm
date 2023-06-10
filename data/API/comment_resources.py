import datetime
from flask import jsonify
from flask_restful import Resource, abort

from data import db_session
from ..user_model import User
from ..post_model import Post
from ..comment_model import Comment
from .comment_reqparse import parser


# Поиск комментария
def abort_if_comment_not_found(comment_id):
    session = db_session.create_session()
    comments = session.query(Comment).get(comment_id)
    if not comments:
        abort(404, message=f"Comment {comment_id} not found")


# Получение одного комментария
class CommentsResource(Resource):
    def get(self, comment_id):
        abort_if_comment_not_found(comment_id)
        session = db_session.create_session()
        comment = session.query(Comment).get(comment_id)
        return jsonify({'comment': comment.to_dict(only=('user_id', 'post_id', 'text', 'create_date'))})


# Удаление комментария (нужен пароль пользователя)
class CommentsDelete(Resource):
    def delete(self, comment_id, password):
        abort_if_comment_not_found(comment_id)
        session = db_session.create_session()
        comment = session.query(Comment).get(comment_id)
        user = session.query(User).get(comment.user_id)
        if user.check_password(password):
            session.delete(comment)
            session.commit()
            return jsonify({'success': 'OK'})
        return abort(404, message=f"Wrong password, access denied")


# Получить все комментарии или создать новый
class CommentsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        comments = session.query(Comment).all()
        return jsonify({'comments': [item.to_dict(only=('id', 'user_id', 'post_id', 'text', 'create_date'))
                                     for item in comments]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        user = session.query(User).get(args["user_id"])
        post = session.query(Post).get(args["post_id"])
        if user and post:
            if user.check_password(args["password"]):
                comment = Comment()
                comment.user_id = user.id
                comment.post_id = post.id
                comment.create_date = datetime.datetime.now()
                comment.text = args["text"]
                session.add(comment)
                session.commit()
                return jsonify({'success': 'OK'})
            return abort(404, message=f"Wrong password, access denied")
        return abort(404, message=f"Wrong post id or user id")
