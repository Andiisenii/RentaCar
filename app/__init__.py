import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import cloudinary

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    # Secret key për sesione, forms, csrf, etj.
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-secret-key-ndersa-eshte-dev')

    # Lidhja me databazën PostgreSQL ose SQLite për zhvillim lokal
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Render përdor 'postgres://', por SQLAlchemy do 'postgresql://'
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url.replace('postgres://', 'postgresql://', 1)
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/db.sqlite3'  # fallback

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    cloudinary.config(
        cloud_name=os.environ.get('dzgtfucjo'),
        api_key=os.environ.get('929372342645252'),
        api_secret=os.environ.get('8r8TJV1Zh92_jFi6sBOuOnN6mII'),
        secure=True
    )


    # Inicializimi i db dhe migrimeve
    db.init_app(app)
    migrate.init_app(app, db)

    # Importo modelet dhe blueprinte për të shmangur errors
    from app import models
    from app.routes_admin import admin as admin_blueprint
    from app.routes import main as main_blueprint

    # Regjistro blueprinte
    app.register_blueprint(main_blueprint)
    app.register_blueprint(admin_blueprint)

    return app
