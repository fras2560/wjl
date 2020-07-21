# -*- coding: utf-8 -*-
""" Holds information that only players of the league can see."""
from flask import render_template
from flask_login import login_required, current_user
from app import wjl_app
from app.views.helper import get_base_data
from app.model import Field, Team, LeagueRequest
from app.errors import NotFoundException


@wjl_app.route("/field/<int:field_id>")
@login_required
def field(field_id: int):
    """A route to view the given field."""
    field = Field.query.get(field_id)
    if field is None:
        raise NotFoundException(f"Sorry, field not found - {field_id}")
    return render_template("field.html",
                           field=field.json(),
                           base_data=get_base_data(),)


@wjl_app.route("/team/<int:team_id>")
@login_required
def team(team_id: int):
    """A route to view the given team."""
    team = Team.query.get(team_id)
    if team is None:
        raise NotFoundException(f"Sorry, team not found - {team_id}")
    team_requests = (LeagueRequest.query
                     .filter(LeagueRequest.email == current_user.email)
                     .filter(LeagueRequest.team_id == team_id)
                     .filter(LeagueRequest.pending == True).count())
    return render_template("team.html",
                           team=team.json(),
                           on_team=current_user in team.players,
                           made_request=team_requests > 0,
                           base_data=get_base_data())
