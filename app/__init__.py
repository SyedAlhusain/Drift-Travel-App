from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = '453685vstja3r5'
# Connect to the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://pascal:uAZg04eUXKhO@ep-tiny-voice-59659868.' \
                                        'us-east-2.aws.neon.tech/neondb?sslmode=require'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from app import routes
