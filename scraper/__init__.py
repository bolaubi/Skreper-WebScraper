from flask import Flask
from flask_mail import Mail
import sqlalchemy as db
import yaml
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)  # initialize flask app
db_yaml = yaml.safe_load(open('db.yaml'))  # credentials
conn = f"mysql://{db_yaml['mysql_user']}:{db_yaml['mysql_password']}@{db_yaml['mysql_host']}/{db_yaml['mysql_db']}"
app.config['SQLALCHEMY_DATABASE_URI'] = conn
app.config['SECRET_KEY'] = db_yaml['secret_key']

# Setting up Flask-Mail
gmail_yaml = yaml.safe_load(open('email_cred.yaml'))
app.config['TESTING'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = f"{gmail_yaml['gmail_u']}"
app.config['MAIL_PASSWORD'] = f"{gmail_yaml['gmail_p']}"
app.config['MAIL_DEFAULT_SENDER'] = f"{gmail_yaml['gmail_u']}"
app.config['MAIL_MAX_EMAILS'] = None
app.config['MAIL_ASCII_ATTACHMENTS'] = False
mail = Mail(app)

# Initialize Flask-SQLAlchemy
dbs = SQLAlchemy(app)

# Initialize Login Manager from flask_login
login_manager = LoginManager(app)
login_manager.login_view = 'login_page'
login_manager.login_message_category = 'info'

# Initialize SQLAlchemy
sqlengine = db.create_engine(conn)
engine = sqlengine.raw_connection()
cursor = engine.cursor() # cursor for execute or fetch data
connection = sqlengine.connect()  # for execute
transac = connection.begin()  # for commit

# Initialize flask_bcrypt
bcrypt = Bcrypt(app)

# Setup dir path for absolute path
dir = os.path.dirname(__file__)

from scraper import routes




