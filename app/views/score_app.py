# -*- coding: utf-8 -*-
"""Holds views related to the score app."""
from flask import render_template, Response, request, url_for
from flask_login import login_required, current_user
from sqlalchemy import not_, or_
from app import wjl_app
from app.views.helper import get_base_data
from app.errors import NotFoundException, LackScorePermissionException
from app.model import Match, Sheet, DB
from app.logging import LOGGER
from app.helpers import tomorrow_date
import json


@wjl_app.route("/submit_score")
@login_required
def submit_score():
    """A route to get matches that one can submit scores for."""
    all_matches = (Match.query
                   .filter(Match.date <= tomorrow_date())
                   .filter(not_(or_(Match.away_team_id == None,
                                    Match.home_team_id == None))))
    if not current_user.is_convenor:
        team_ids = [team.id for team in current_user.teams]
        all_matches = (all_matches.filter(or_(
                Match.away_team_id.in_(team_ids),
                Match.home_team_id.in_(team_ids))))
    all_matches = all_matches.all()
    submitted_matches = []
    outstanding_matches = []
    for match in all_matches:
        match_data = match.json()
        match_data["submit_link"] = url_for("submit_sheet", match_id=match.id)
        match_data["edit_link"] = url_for("edit_sheet", match_id=match.id)
        if match.has_sheets():
            submitted_matches.append(match_data)
        else:
            outstanding_matches.append(match_data)
    return render_template("pick_match_to_submit.html",
                           base_data=get_base_data(),
                           outstanding_matches=outstanding_matches,
                           submitted_matches=submitted_matches)


@wjl_app.route("/submit_sheet/<int:match_id>")
@login_required
def submit_sheet(match_id: int):
    """A route to submit a gamesheet for some match."""
    match = Match.query.get(match_id)
    if match is None:
        raise NotFoundException(f"Unable to find match - {match_id}")
    if not current_user.can_submit_scores(match):
        raise LackScorePermissionException(
            f"Not part of either team - {match_id}")
    return render_template("submit_sheet.html",
                           base_data=get_base_data(),
                           match=match.json(),
                           match_link=url_for('match', match_id=match.id),
                           save_link=url_for("save_sheet"))


@wjl_app.route("/save_sheet", methods=["POST"])
@login_required
def save_sheet():
    """Save the given gamesheet."""
    sheet = None
    try:
        sheet = request.get_json(silent=True)
        saved_sheet = Sheet.from_json(sheet)
        DB.session.add(saved_sheet)
        DB.session.commit()
        LOGGER.info(
            f"{current_user} saved sheet {sheet}")
        return Response(json.dumps(saved_sheet.json()),
                        status=200, mimetype="application/json")
    except NotFoundException as error:
        LOGGER.warning(
            f"{current_user} tried saving sheet for match that d.n.e {sheet}")
        return Response(json.dumps(error),
                        status=404, mimetype="application/json")


@wjl_app.route("/edit_sheet/<int:match_id>")
@login_required
def edit_sheet(match_id: int):
    """A route to edit a match's gamesheets."""
    match = Match.query.get(match_id)
    if match is None:
        raise NotFoundException("Unable to find match {match_id}")
    if not current_user.can_submit_scores(match):
        raise LackScorePermissionException("Not part of team")
    return render_template("edit_sheet.html",
                           base_data=get_base_data(),
                           match=match)
