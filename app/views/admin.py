# -*- coding: utf-8 -*-
"""Holds views that are used by an administrator."""
from flask import render_template, url_for, Response
from flask_login import login_required, current_user
from app import wjl_app
from app.authentication import admin_required, api_admin_required
from app.model import Session, Player, Team, LeagueRequest, DB
from app.errors import NotFoundException
from app.logging import LOGGER
from app.views.helper import get_base_data
from app.views.types import PendingRequest
import json


@wjl_app.route("/edit_games")
@login_required
@admin_required
def pick_session_to_edit():
    sessions = [sesh.json() for sesh in Session.query.all()]
    return render_template("select_session.html",
                           base_data=get_base_data(),
                           sessions=sessions)


@wjl_app.route("/edit_games/<int:session_id>")
@login_required
@admin_required
def edit_games_in_session(session_id):
    sesh = Session.query.get(session_id)
    if sesh is None:
        raise NotFoundException("Sorry, session not found - {session_id}")
    match_link = url_for("get_matches_in_session", session_id=sesh.id)
    return render_template("edit_matches_in_session.html",
                           base_data=get_base_data(),
                           session=sesh,
                           fields_link=url_for("get_all_fields"),
                           matches_link=match_link,
                           teams_link=url_for("get_all_teams"),
                           save_match_link=url_for("save_match"))


@wjl_app.route("/pending_requests")
@login_required
@admin_required
def check_league_requests():
    pending_requests = [PendingRequest.get_request(pending)
                        for pending in LeagueRequest.query.filter(
                            LeagueRequest.pending == True).all()]
    return render_template("league_requests.html",
                           base_data=get_base_data(),
                           pending_requests=pending_requests)


@wjl_app.route("/pending_requests/<int:request_id>/<decision>")
@api_admin_required
def league_request_decision(request_id: int, decision: str):
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
        player = Player(league_request.email, league_request.name)
        team.add_player(player)
        DB.session.delete(league_request)
        DB.session.commit()
    else:
        # decline the request and save to database
        league_request.decline_request()
        DB.session.commit()
    return Response(json.dumps(None), status=200, mimetype="application/json")
