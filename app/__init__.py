from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
import os
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()  # Shtojmë migratet

def create_app():
    load_dotenv()  # ngarko env variables nga .env (lokalisht)
    app = Flask(__name__)
    
    # Vendos echo true vetëm në development
    app.config['SQLALCHEMY_ECHO'] = os.environ.get('FLASK_ENV') == 'development'
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'sekreti')

    # Lësho connection string për databazën nga env var
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        database_url = 'sqlite:///db.sqlite3'  # fallback dev lokal
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'app/static/uploads'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from .routes_public import public
    from .routes_admin import admin
    from app.templates.main.routes import main

    app.register_blueprint(main)
    app.register_blueprint(admin, url_prefix='/admin')

    with app.app_context():
        # Mos e përdor db.create_all kur përdor migrime
        pass

    return app

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))

from app import models
