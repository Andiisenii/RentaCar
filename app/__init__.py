import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import cloudinary
import cloudinary.uploader
import cloudinary.api

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-secret-key-ndersa-eshte-dev')
    # Përdor PostgreSQL nëse DATABASE_URL ekziston, përndryshe SQLite (për dev)
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Rregullo URL (Render përdor 'postgres://', SQLAlchemy do 'postgresql://')
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url.replace('postgres://', 'postgresql://', 1)
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/db.sqlite3'  # opsionale fallback

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    
    cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET'),
    secure=True
)

    db.init_app(app)
    migrate.init_app(app, db)  # <-- Kjo mungonte tek ti

    from app import models
    from app.routes_admin import admin as admin_blueprint
    from app.routes import main
    
    app.register_blueprint(main) 
    app.register_blueprint(admin_blueprint)
    return app
