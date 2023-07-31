from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_login import LoginManager
from flask_migrate import Migrate
import cloudinary

app = Flask(__name__)
app.config['SECRET_KEY'] = '275b8f33ac0f1fdda19e5b9f070c27e9'
app.config['SECURITY_PASSWORD_SALT'] = "hadialvi"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'hadi.alvi@devsinc.com'
app.config['MAIL_PASSWORD'] = 'tjwnxhehtowvqzia'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_DEFAULT_SENDER'] = 'hadi.alvi@devsinc.com'
cloudinary.config(
    cloud_name='djbu7u6rk',
    api_key='917172745412816',
    api_secret='K1pYEL-iUeox4yCOVNR8DIdpvFA'
)

#create email instance
mail = Mail(app)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
migrate = Migrate(app,db,render_as_batch=True)

from blog_app import routes
