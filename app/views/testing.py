# -*- coding: utf-8 -*-
"""Holds views that are only used for testing."""
from flask import Response, request
from flask_login import login_user
from functools import wraps
from app import wjl_app
from app.model import Player, DB
from app.logging import LOGGER
import json


def requires_testing(f):
    """A decorator for routes that only available while testing"""
    @wraps(f)
    def decorated(*args, **kwargs):
        are_testing = wjl_app.config['ARE_TESTING']
        if are_testing is None or not are_testing:
            return Response("Testing feature not on", 400)
        return f(*args, **kwargs)
    return decorated


@wjl_app.route("/testing/api/create_and_login", methods=["POST"])
@requires_testing
def create_and_login():
    player_info = request.get_json(silent=True)
    convenor = (player_info.get("is_convenor", False) or
                player_info.get("isConvenor", False))
    LOGGER.info(f"Adding player to league: {player_info}")
    player = Player(player_info.get("email"),
                    name=player_info.get("name", None),
                    is_convenor=convenor)
    DB.session.add(player)
    DB.session.commit()
    login_user(player)
    return Response(json.dumps(player.json()), 200)
