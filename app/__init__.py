from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = '453685vstja3r5'
# Connect to the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://husainsalamdar786:S9sIUkHC7XyP@ep-hidden-union-07506131.us-east-2.aws.neon.tech/Rove-Travel-App?sslmode=require'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from app import routes


