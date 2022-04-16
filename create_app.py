import os

from flask import Flask
from flask_login import LoginManager
from flask_restful import Api

from data import db_session
from data.API import user_resources, post_resources, comment_resources
from data.db_session import global_init
from data.user_model import User


def create_app():
    app = Flask(__name__)
    api = Api(app)
    app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
    file_path = os.path.join(app.root_path, 'db', 'NewGramm.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + file_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['PROPAGATE_EXCEPTIONS'] = True
    global_init(file_path)
    login_manager = LoginManager()
    login_manager.init_app(app)
    api.add_resource(user_resources.UsersListResource, '/api/users')
    api.add_resource(user_resources.UsersResource, '/api/users/<int:user_id>')
    api.add_resource(user_resources.UsersDelete, '/api/users/<int:user_id>/<string:password>')

    api.add_resource(post_resources.PostsListResource, '/api/posts')
    api.add_resource(post_resources.PostsResource, '/api/posts/<int:post_id>')
    api.add_resource(post_resources.PostsDelete, '/api/posts/<int:post_id>/<string:password>')

    api.add_resource(comment_resources.CommentsListResource, '/api/comments')
    api.add_resource(comment_resources.CommentsResource, '/api/comments/<int:comment_id>')
    api.add_resource(comment_resources.CommentsDelete, '/api/comments/<int:comment_id>/<string:password>')

    @login_manager.user_loader
    def load_user(user_id):
        db_sess = db_session.create_session()
        return db_sess.query(User).get(user_id)

    return app
