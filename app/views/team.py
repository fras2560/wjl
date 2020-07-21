# -*- coding: utf-8 -*-
"""Holds Views and APIs related to team and team requests"""

from flask import render_template, Response, request
from flask_login import login_required, current_user
from app import wjl_app
from app.authentication import api_player_required
from app.model import Player, Team, LeagueRequest, DB
from app.logging import LOGGER
from app.views.helper import get_base_data
from app.views.types import PendingRequest
import json


@wjl_app.route("/api/team/registration", methods=["POST"])
@api_player_required
def registration_for_team():
    team_request = request.get_json(silent=True)
    team = Team.query.get(team_request.get('team_id'))
    player = Player.query.get(team_request.get('player_id'))
    joining = team_request.get('register')
    if team is None:
        return Response(json.dumps(team_request.get('team_id')), status=404,
                        mimetype="application/json")
    elif player is None:
        return Response(json.dumps(team_request.get('player_id')), status=404,
                        mimetype="application/json")
    # able to make request only for themself unless they are a convenor
    if not current_user.is_convenor and player.id != current_user.id:
        return Response(json.dumps("Unable to make request for other player"),
                        status=401,
                        mimetype="application/json")
    if joining:
        DB.session.add(
            LeagueRequest(current_user.email, current_user.name, team))
        msg = (f"{current_user} player {player.name}"
               f"requested to join team {team.name}")
        LOGGER.info(msg)
    else:
        team.remove_player(player)
        LOGGER.info(f"{current_user} player {player.id} left team {team.id}")
    DB.session.commit()
    return Response(json.dumps(team.json()), status=200,
                    mimetype="application/json")


@wjl_app.route("/pending_requests")
@login_required
def pending_requests():
    if current_user.is_convenor:
        # convenor can respond to all requests
        pending_requests = [PendingRequest.get_request(pending)
                            for pending in LeagueRequest.query.filter(
                                LeagueRequest.pending == True).all()]
    else:
        # can only respond to teams requests
        my_requests = LeagueRequest.query.filter(LeagueRequest.pending == True)
        for team in current_user.teams:
            my_requests = my_requests.filter(LeagueRequest.team_id == team.id)
        if len(current_user.teams) > 0:
            pending_requests = [PendingRequest.get_request(pending)
                                for pending in my_requests.all()]
        else:
            pending_requests = []
    return render_template("league_requests.html",
                           base_data=get_base_data(),
                           pending_requests=pending_requests)


@wjl_app.route("/pending_requests/<int:request_id>/<decision>")
@api_player_required
def pending_requests_decision(request_id: int, decision: str):
    league_request = LeagueRequest.query.get(request_id)
    if league_request is None:
        LOGGER.warning(
            f"{current_user} looking at league request {request_id} dne")
        return Response(json.dumps(None), status=404,
                        mimetype="application/json")
    if decision.lower().strip() == "accept":
        team = Team.query.get(league_request.team_id)
        if team is None:
            msg = f"Team does not exist {league_request.team_id}"
            LOGGER.warning(
                f"{current_user} {msg}")
            return Response(msg, status=400, mimetype="application/json")
        # see if player already exists
        # create them if they dont already
        player = Player.query.filter(
            Player.email == league_request.email).first()
        if player is None:
            player = Player(league_request.email, league_request.name)
        team.add_player(player)
        DB.session.delete(league_request)
        DB.session.commit()
    else:
        # decline the request and save to database
        league_request.decline_request()
        DB.session.commit()
    return Response(json.dumps(None), status=200, mimetype="application/json")
