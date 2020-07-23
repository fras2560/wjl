# -*- coding: utf-8 -*-
"""Holds views that are used by an administrator."""
from flask import render_template, url_for
from flask_login import login_required
from app import wjl_app
from app.authentication import admin_required
from app.model import Session
from app.errors import NotFoundException
from app.views.helper import get_base_data


@wjl_app.route("/edit_games")
@login_required
@admin_required
def edit_games():
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
