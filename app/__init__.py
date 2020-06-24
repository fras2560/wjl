import os
from flask import Flask
from flask_dance.contrib.github import make_github_blueprint
from flask_dance.contrib.facebook import make_facebook_blueprint
from flask_dance.contrib.google import make_google_blueprint
from flask_sqlalchemy import SQLAlchemy
from uuid import uuid1

# initialize the app
wjl_app = Flask(__name__)


# get all the environment variables
URL = os.environ.get("DATABASE_URL", "sqlite://")
SECRET_KEY = os.environ.get("SECRET_KEY", str(uuid1()))
GITHUB_CLIENT_ID = os.environ.get("GITHUB_OAUTH_CLIENT_ID", "")
GITHUB_CLIENT_SECRET = os.environ.get("GITHUB_OAUTH_CLIENT_SECRET", "")
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_OAUTH_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET", "")
FACEBOOK_CLIENT_ID = os.environ.get("FACEBOOK_OAUTH_CLIENT_ID", "")
FACEBOOK_CLIENT_SECRET = os.environ.get("FACEBOOK_OAUTH_CLIENT_SECRET", "")

# configure the app for all the keys & secrets, database
wjl_app.config.from_object(__name__)
wjl_app.secret_key = SECRET_KEY
wjl_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
wjl_app.config["SECRET_KEY"] = SECRET_KEY
wjl_app.config["SQLALCHEMY_DATABASE_URI"] = URL
wjl_app.config["GITHUB_OATUH_CLIENT_ID"] = GITHUB_CLIENT_ID
wjl_app.config["GITHUB_OATUH_CLIENT_SECRET"] = GITHUB_CLIENT_SECRET
wjl_app.config["GOOGLE_OATUH_CLIENT_ID"] = GOOGLE_CLIENT_ID
wjl_app.config["GOOGLE_OATUH_CLIENT_SECRET"] = GOOGLE_CLIENT_SECRET
wjl_app.config["FACEBOOK_OATUH_CLIENT_ID"] = FACEBOOK_CLIENT_ID
wjl_app.config["FACEBOOK_OATUH_CLIENT_SECRET"] = FACEBOOK_CLIENT_SECRET

# setup the database
DB = SQLAlchemy(wjl_app)

# register the all the blueprints
wjl_app.register_blueprint(
    make_github_blueprint(client_id=GITHUB_CLIENT_ID,
                          client_secret=GITHUB_CLIENT_SECRET),
    url_prefix="/login")
wjl_app.register_blueprint(
    make_google_blueprint(scope=["profile", "email"],
                          client_id=GOOGLE_CLIENT_ID,
                          client_secret=GOOGLE_CLIENT_SECRET),
    url_prefix="/login")
wjl_app.register_blueprint(
    make_facebook_blueprint(client_id=FACEBOOK_CLIENT_ID,
                            client_secret=FACEBOOK_CLIENT_SECRET),
    url_prefix="/login")


from app.views import *
