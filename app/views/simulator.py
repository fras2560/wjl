# -*- coding: utf-8 -*-
"""Holds views related to game simulator app."""
from typing import TypedDict
from flask import render_template, Response
from app import wjl_app
from app.views.helper import get_active_session, get_base_data
from app.model import Match, Sheet, Team
from app.logging import LOGGER
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


@wjl_app.route("/simulator/team/model/<int:team_id>/<int:difficulty>", methods=["GET"])
def team_simulation_model(team_id: int, difficulty: int):

    return Response(json.dumps(get_team_model(team_id, difficulty)),
                        status=200, mimetype="application/json")


class TeamSimulation(TypedDict):
    """A model for a team simulation."""
    slot: float
    dingers: float
    deuces: float
    jams: float
    miss: float


def pull_team_stats(team_id: int, sheet: Sheet, match: Match) -> dict:
    """Return the team stats from the given sheet."""
    if (team_id == match.away_team_id):
        my_throws = sheet.away_jams +  sheet.away_deuces + sheet.away_dingers + (1 if sheet.away_slot else 0)
        their_throws = sheet.home_jams +  sheet.home_deuces + sheet.home_dingers + (1 if sheet.home_slot else 0)
        return {
            'slot': 1 if sheet.away_slot else 0,
            'jam': sheet.away_jams,
            'deuce': sheet.away_deuces,
            'dinger': sheet.away_dingers,
            'miss': 0 if my_throws > their_throws else their_throws - my_throws
        }
    else:
        my_throws = sheet.home_jams +  sheet.home_deuces + sheet.home_dingers + (1 if sheet.home_slot else 0)
        their_throws = sheet.away_jams +  sheet.away_deuces + sheet.away_dingers + (1 if sheet.away_slot else 0)
        return {
            'slot': 1 if sheet.home_slot else 0,
            'jam': sheet.home_jams,
            'deuce': sheet.home_deuces,
            'dinger': sheet.home_dingers,
            'miss': 0 if my_throws > their_throws else their_throws - my_throws
        }


def get_team_model(team_id: int, difficulty: int) -> TeamSimulation:
    """Return the team simulation model"""
    sess = get_active_session()
    matches = Match.query.filter(Match.session_id == sess.id).all()
    model = {
        "slot": 0,
        "dinger": 0,
        "jam": 0,
        "miss": 0,
        'deuce': 0
    }
    total_throws = 0
    for match in matches:
        for sheet in match.sheets:
            stats = pull_team_stats(team_id, sheet, match)
            model['slot'] += stats['slot']
            model['jam'] += stats['jam']
            model['deuce'] += stats['deuce']
            model['dinger'] += stats['dinger']
            model['miss'] += stats['miss'] + difficulty
            total_throws += stats['slot'] + stats['jam'] + stats['deuce'] + stats['dinger'] + stats['miss'] + difficulty
    print(model)
    model['slot'] = max(round(model['slot'] / total_throws, 5), 0.01)
    model['dinger'] = max(round(model['dinger'] / total_throws, 5), 0.05)
    model['deuce'] = max(round(model['deuce'] / total_throws, 5), 0.05)
    model['jam'] = max(round(model['jam'] / total_throws, 5), 0.05)
    model['miss'] = 1 - model['deuce'] - model['jam'] - model['dinger'] - model['slot']
    LOGGER.info(f"A simulation is happening against team - {team_id}")
    LOGGER.info(model)
    return model
