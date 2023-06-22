from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_wtf import CSRFProtect

db = SQLAlchemy()
mail = Mail()
csrf = CSRFProtect()
