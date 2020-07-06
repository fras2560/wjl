# -*- coding: utf-8 -*-
"""The main entry into the website"""
from flask import Flask
from app.authentication import github_blueprint, facebook_blueprint,\
    google_blueprint, login_manager
from app.config import Config
from app.model import DB

# initialize the app
wjl_app = Flask(__name__)
wjl_app.config.from_object(Config)

# register the all the blueprints
wjl_app.register_blueprint(github_blueprint, url_prefix="/login")
wjl_app.register_blueprint(facebook_blueprint, url_prefix="/login")
wjl_app.register_blueprint(google_blueprint, url_prefix="/login")

# init DB and login manager
DB.init_app(wjl_app)
login_manager.init_app(wjl_app)

# needs to be imported at end to avoid circular dependency
from app.views import *
from app.error_handling import handle_generic_error
