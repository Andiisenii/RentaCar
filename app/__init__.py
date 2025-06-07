import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # Përdor PostgreSQL nëse DATABASE_URL ekziston, përndryshe SQLite (për dev)
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Rregullo URL (Render përdor 'postgres://', SQLAlchemy do 'postgresql://')
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url.replace('postgres://', 'postgresql://', 1)
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/db.sqlite3'  # opsionale fallback

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)  # <-- Kjo mungonte tek ti

    from app import models
    from app.routes import main
    app.register_blueprint(main) 

    return app
