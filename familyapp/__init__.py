from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

env = "dev"
if env == "dev":
    app.debug = True
    app.config["SECRET_KEY"] = "familywebsiteissimple"
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:Postgre-arj4703@localhost/familydatabase"
else:
    app.debug = False
    app.config["SECRET_KEY"] = os.environ["secret"]
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

db = SQLAlchemy(app)

from familyapp import routes
