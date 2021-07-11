from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

env = "prod"
if env == "dev":
    app.debug = True
    app.config["SECRET_KEY"] = "familywebsiteissimple"
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:Postgre-arj4703@localhost/familydatabase"
else:
    app.debug = False
    app.config["SECRET_KEY"] = os.environ["secret"]
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://nxsvptdeqefttg:0f049899f41b857f9d99175b915a237fd008a3cedb2b94e731af79684c4c2510@ec2-34-195-143-54.compute-1.amazonaws.com:5432/d70fr7k9if8sim"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

db = SQLAlchemy(app)

from familyapp import routes
