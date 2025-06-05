from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rentacar.db'
    app.config['SECRET_KEY'] = 'sekreti'

    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        from app import routes, models  # importo këtu për të shmangur circular import

        db.create_all()

    return app

@login_manager.user_loader
def load_user(user_id):
    from app.models import User  # importo këtu për të shmangur circular import
    return User.query.get(int(user_id))
