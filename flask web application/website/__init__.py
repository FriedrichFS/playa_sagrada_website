from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_mail import Mail, Message
import pyrebase

config = {
    'apiKey': "AIzaSyAOP6-li3gbt-cxfZBozfjwxtJNe8PvrT8",
    'authDomain': "mediceoarbeitszeiten.firebaseapp.com",
    'projectId': "mediceoarbeitszeiten",
    'storageBucket': "mediceoarbeitszeiten.appspot.com",
    'messagingSenderId': "647902816076",
    'appId': "1:647902816076:web:dd1154ef5daa1508ccd1e9",
    'measurementId': "G-1N1FX7J4SV",
    'databaseURL': ''
}


db = SQLAlchemy()
DB_NAME = "database.db"


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "6uW5lneiTO"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    from .views import views
    from .auth import auth
    from .models import User, Arbeit

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    return app


def create_database(app):
    if not path.exists('./' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')
