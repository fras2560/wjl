# -*- coding: utf-8 -*-
"""Holds views related to game simulator app."""
from typing import TypedDict
from flask import render_template, Response, request, url_for
from flask_login import login_required, current_user
from sqlalchemy import not_, or_
from app import wjl_app
from app.authentication import api_score_required
from app.views.helper import get_base_data
from app.errors import NotFoundException, LackScorePermissionException
from app.model import Match, Sheet, DB, Team
from app.logging import LOGGER
from app.helpers import tomorrow_date
import json

@wjl_app.route("/simulator/pick-team")
def pick_team():
    teams = [team.json() for team in Team.query.all()]
    return render_template("select_team_simulator.html",
                           base_data=get_base_data(),
                           teams=teams)


@wjl_app.route("/simulator/team/<int:team_id>/<int:difficulty>")
def simulate_game(team_id: int, difficulty: int):
    team = Team.query.get(team_id)
    return render_template("simulate_team.html",
                           base_data=get_base_data(),
                           team = team.json(),
                           team_id=team_id,
                           difficulty=difficulty)


@wjl_app.route("/simulator/team/model/<int:team_id>", methods=["GET"])
def team_simulation_model(team_id: int):

    return Response(json.dumps(get_team_model(team_id)),
                        status=200, mimetype="application/json")


class TeamSimulation(TypedDict):
    """A model for a team simulation."""
    slot: float
    dingers: float
    deuces: float
    jams: float
    miss: float


def get_team_model(team_id: int) -> TeamSimulation:
    """Return the team simulation model"""
    return {
        "slot": 0.01,
        "dinger": 0.33,
        "deuce": 0.33,
        "jam": 0.16,
        "miss": 0.17
    }
