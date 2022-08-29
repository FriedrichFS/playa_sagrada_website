from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_mail import Mail, Message
import pyrebase


db = SQLAlchemy()
DB_NAME = "database.db"
config = {
    "apiKey": "AIzaSyA05NzVjcRpr9Z1mKL4ij5HhdiKzeGcuw8",
    "authDomain": "playasagrada-9db3b.firebaseapp.com",
    "projectId": "playasagrada-9db3b",
    "storageBucket": "playasagrada-9db3b.appspot.com",
    "messagingSenderId": "521917073602",
    "appId": "1:521917073602:web:77d03ecded8644707a535b",
    "measurementId": "G-MXKM0KL8M0"

}

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "6uW5lneiTO"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    firebase = pyrebase.initialize_app(config)
    auth = firebase.auth()
    
    

    from .views import views
    from .auth import auth
    from .models import User, Arbeit    


    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    app.register_blueprint(views, url_prefix = "/")
    app.register_blueprint(auth, url_prefix = "/")

    return app
