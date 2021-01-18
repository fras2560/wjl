# -*- coding: utf-8 -*-
"""Holds APIs used by the front end"""
from flask import Response, request
from flask_login import current_user
from sqlalchemy import asc
from app import wjl_app
from app.errors import NotFoundException
from app.model import Session, Match, Team, Field, DB
from app.logging import LOGGER
from app.views.types import ScheduleRecord
from app.authentication import api_admin_required, api_player_required
from sqlalchemy.exc import IntegrityError

import json


@wjl_app.route("/api/field/save", methods=["POST", "PUT"])
@api_admin_required
def save_field():
    field = None
    try:
        field = request.get_json(silent=True)
        LOGGER.debug(f"Save/Update field {field}")
        saved_field = Field.from_json(field)
        if field.get("id", None) is None:
            DB.session.add(saved_field)
        DB.session.commit()
        LOGGER.info(
            f"{current_user} saved field {field}")
        return Response(json.dumps(saved_field.json()),
                        status=200, mimetype="application/json")
    except NotFoundException as error:
        msg = str(error)
        LOGGER.warning(
            f"{current_user} tried saving field but issue {msg}")
        return Response(json.dumps(msg),
                        status=404, mimetype="application/json")
    except IntegrityError as error:
        DB.session.rollback()
        msg = str(error)
        LOGGER.warning(
            f"{current_user} tried saving field but issue {msg}")
        return Response(json.dumps(msg),
                        status=400, mimetype="application/json")


@wjl_app.route("/api/team/save", methods=["POST", "PUT"])
@api_admin_required
def save_team():
    team = None
    try:
        team = request.get_json(silent=True)
        LOGGER.debug(f"Save/Update team {team}")
        saved_team = Team.from_json(team)
        if team.get("id", None) is None:
            DB.session.add(saved_team)
        DB.session.commit()
        LOGGER.info(
            f"{current_user} saved team {team}")
        return Response(json.dumps(saved_team.json()),
                        status=200, mimetype="application/json")
    except NotFoundException as error:
        msg = str(error)
        LOGGER.warning(
            f"{current_user} tried saving team but issue {msg}")
        return Response(json.dumps(msg),
                        status=404, mimetype="application/json")
    except IntegrityError as error:
        DB.session.rollback()
        msg = str(error)
        LOGGER.warning(
            f"{current_user} tried saving team but issue {msg}")
        return Response(json.dumps(msg),
                        status=400, mimetype="application/json")


@wjl_app.route("/api/session/save", methods=["POST", "PUT"])
@api_admin_required
def save_session():
    sesh = None
    try:
        sesh = request.get_json(silent=True)
        LOGGER.debug(f"Save/Update session {sesh}")
        saved_session = Session.from_json(sesh)
        if sesh.get("id", None) is None:
            DB.session.add(saved_session)
        DB.session.commit()
        LOGGER.info(
            f"{current_user} saved session {saved_session}")
        return Response(json.dumps(saved_session.json()),
                        status=200, mimetype="application/json")
    except NotFoundException as error:
        msg = str(error)
        LOGGER.warning(
            f"{current_user} tried saving session but issue {msg}")
        return Response(json.dumps(msg),
                        status=404, mimetype="application/json")
    except IntegrityError as error:
        DB.session.rollback()
        msg = str(error)
        LOGGER.warning(
            f"{current_user} tried saving session but issue {msg}")
        return Response(json.dumps(msg),
                        status=400, mimetype="application/json")


@wjl_app.route("/api/match/save", methods=["POST", "PUT"])
@api_admin_required
def save_match():
    match = None
    try:
        match = request.get_json(silent=True)
        LOGGER.debug(f"Save/Update match {match}")
        saved_match = Match.from_json(match)
        if match.get("id", None) is None:
            DB.session.add(saved_match)
        DB.session.commit()
        LOGGER.info(
            f"{current_user} saved match {match}")
        return Response(json.dumps(saved_match.json()),
                        status=200, mimetype="application/json")
    except NotFoundException as error:
        msg = str(error)
        LOGGER.warning(
            f"{current_user} tried saving match but issue {msg}")
        return Response(json.dumps(msg),
                        status=404, mimetype="application/json")
    except IntegrityError as error:
        DB.session.rollback()
        msg = str(error)
        LOGGER.warning(
            f"{current_user} tried saving match but issue {msg}")
        return Response(json.dumps(msg),
                        status=400, mimetype="application/json")


@wjl_app.route("/api/team/<int:team_id>")
@api_player_required
def get_team(team_id):
    team = Team.query.get(team_id)
    if team is None:
        return Response(json.dumps(team_id), status=404,
                        mimetype="application/json")
    return Response(json.dumps(team.json()), status=200,
                    mimetype="application/json")


@wjl_app.route("/api/teams")
@api_player_required
def get_all_teams():
    teams = [team.json() for team in Team.query.all()]
    return Response(json.dumps(teams), status=200, mimetype="application/json")


@wjl_app.route("/api/fields")
@api_player_required
def get_all_fields():
    fields = [field.json() for field in Field.query.all()]
    return Response(json.dumps(fields), status=200,
                    mimetype="application/json")


@wjl_app.route("/api/session/<int:session_id>/matches")
@api_player_required
def get_matches_in_session(session_id):
    sesh = Session.query.get(session_id)
    if sesh is None:
        return Response(json.dumps(None), status=404,
                        mimetype="application/json")
    matches = (Match.query
               .filter(Match.session_id == session_id)
               .order_by(asc(Match.date)).all())
    matches_data = [ScheduleRecord.create_schedule_record(match)
                    for match in matches]
    return Response(json.dumps(matches_data), status=200,
                    mimetype="application/json")


@wjl_app.route("/api/session")
def get_all_sessions():
    seshes = [sesh.json() for sesh in Session.query.all()]
    return Response(json.dumps(seshes), status=200,
                    mimetype="application/json")


@wjl_app.route("/api/match/<int:match_id>")
@api_player_required
def get_match(match_id):
    match = Match.query.get(match_id)
    if match is None:
        LOGGER.warning(
            f"{current_user} tried accessing non-existent match {match_id}")
        return Response(None, status=404, mimetype="application/json")
    match_data = match.json()
    sheets = []
    for sheet in match.sheets:
        sheets.append(sheet.json())
    sheets.sort(key=lambda sheet: sheet['id'])
    match_data["sheets"] = sheets
    return Response(json.dumps(match_data),
                    status=200, mimetype="application/json")
