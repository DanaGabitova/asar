import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv


db = SQLAlchemy()
load_dotenv()


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = f'{os.getenv("SECRET_KEY")}'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.getenv("DB_NAME")}'

    db.init_app(app)
    from .views import views
    from .auth import auth
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    from .models import User, Note
    create_database(app)
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    return app


def create_database(app):
    """создание базы данных, если ее не существует"""
    if not os.path.exists(f'website/{os.getenv("DB_NAME")}'):
        db.create_all(app=app)
