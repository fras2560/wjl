# -*- coding: utf-8 -*-
"""Holds views that are related to the standings page."""
from flask import render_template, Response
from flask_login import current_user
from sqlalchemy import or_, not_
from app import wjl_app
from app.views.helper import get_active_session, get_base_data
from app.views.types import TeamRecord
from app.model import Session, Match, Sheet, WhichTeam
from app.logging import LOGGER
import json


@wjl_app.route("/standings")
def standings():
    """A route to get the standings table."""
    league_sessions = [sesh.json() for sesh in Session.query.all()]
    active_session = get_active_session()
    active_session = (active_session
                      if active_session is not None
                      else league_sessions[-1])
    return render_template("standings.html",
                           base_data=get_base_data(),
                           league_sessions=league_sessions,
                           active_session=active_session)


@wjl_app.route("/standings/<int:session_id>")
def standing_table(session_id: int):
    """An API that gets the standings table for the given session."""
    sesh = Session.query.get(session_id)
    if sesh is None:
        LOGGER.warning(
            f"{current_user} looking at standings session {session_id} dne")
        return Response(json.dumps(None), status=404,
                        mimetype="application/json")
    matches = (Match.query
               .filter(Match.session_id == session_id)
               .filter(not_(or_(Match.away_team_id == None,
                            Match.home_team_id == None))).all())
    teams = {}
    for match in matches:
        if match.away_team_id not in teams.keys():
            teams[match.away_team_id] = TeamRecord.empty_record(
                match.away_team_id,
                match.away_team.name)
        if match.home_team_id not in teams.keys():
            teams[match.home_team_id] = TeamRecord.empty_record(
                match.home_team_id,
                match.home_team.name)
        for sheet in Sheet.query.filter(Sheet.match_id == match.id):
            teams[match.away_team_id]["points_scored"] += sheet.away_score
            teams[match.home_team_id]["points_scored"] += sheet.home_score
            teams[match.away_team_id]["jams"] += sheet.away_jams
            teams[match.home_team_id]["jams"] += sheet.home_jams
            teams[match.away_team_id]["slots"] += sheet.away_slot
            teams[match.home_team_id]["slots"] += sheet.home_slot
            teams[match.away_team_id]["games_played"] += 1
            teams[match.home_team_id]["games_played"] += 1
            if sheet.who_won() == WhichTeam.AWAY_TEAM:
                teams[match.away_team_id]['wins'] += 1
                teams[match.home_team_id]['losses'] += 1
            else:
                teams[match.home_team_id]['wins'] += 1
                teams[match.away_team_id]['losses'] += 1
    team_records = list(teams.values())
    team_records = sorted(team_records, reverse=True,
                          key=lambda x: x["wins"] / max(1, x["games_played"]))
    return Response(json.dumps(team_records),
                    status=200, mimetype="application/json")
