from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()  # 💌 initialize mail here

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    mail.init_app(app)  # 💌 bind mail to the app
    login_manager.init_app(app)
    migrate = Migrate(app, db)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .routes import main
    app.register_blueprint(main)

    return app
