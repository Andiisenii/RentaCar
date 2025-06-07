from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from os import path
from dotenv import load_dotenv
import os
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()  # Shtojmë migratet

def create_app():
    load_dotenv()  # ngarko env variables
    app = Flask(__name__)
    app.config['SQLALCHEMY_ECHO'] = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'sekreti')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'app/static/uploads'  # Rruga relative
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
    app.secret_key = 'supersekretkey'
    db.init_app(app)
    migrate.init_app(app, db)  # inicializo migratet me app dhe db
    login_manager.init_app(app)

    # Importo Blueprints këtu, për të shmangur circular import
    from .routes_public import public
    from .routes_admin import admin
    from app.templates.main.routes import main

    app.register_blueprint(main)
    app.register_blueprint(admin, url_prefix='/admin')
    

    with app.app_context():
        db.create_all()  # mund ta heqesh këtë pasi përdor migrimet

    return app

@login_manager.user_loader
def load_user(user_id):
    from app.models import User  # Importo këtu për të shmangur circular import
    return User.query.get(int(user_id))

from app import models
