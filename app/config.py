# -*- coding: utf-8 -*-
"""Holds configuration for the app."""
import os
from uuid import uuid1


class Config(object):
    URL = os.environ.get("DATABASE_URL", "sqlite://")
    SECRET_KEY = os.environ.get("SECRET_KEY", str(uuid1()))
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite://")
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GOOGLE_OAUTH_CLIENT_ID = os.environ.get("GOOGLE_OAUTH_CLIENT_ID", "")
    GOOGLE_OAUTH_CLIENT_SECRET = os.environ.get(
        "GOOGLE_OAUTH_CLIENT_SECRET", "")
    FACEBOOK_OAUTH_CLIENT_ID = os.environ.get("FACEBOOK_OAUTH_CLIENT_ID", "")
    FACEBOOK_OAUTH_CLIENT_SECRET = os.environ.get(
        "FACEBOOK_OAUTH_CLIENT_SECRET", "")
    GITHUB_OAUTH_CLIENT_ID = os.environ.get("GITHUB_OAUTH_CLIENT_ID", "")
    GITHUB_OAUTH_CLIENT_SECRET = os.environ.get(
        "GITHUB_OAUTH_CLIENT_SECRET", "")
    USE_SESSION_FOR_NEXT = True
    ARE_TESTING = os.environ.get("ARE_TESTING", False)
