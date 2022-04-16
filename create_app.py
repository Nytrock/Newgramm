from flask import Flask
from flask_login import LoginManager
from flask_restful import Api

from data.db_session import global_init


def create_app():
    app = Flask(__name__)
    api = Api(app)
    global_init("db/Newgramm.db")
    app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
    login_manager = LoginManager()
    login_manager.init_app(app)
    return app, api, login_manager
