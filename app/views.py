from typing import TypedDict
from flask_login import logout_user, login_required
from flask import render_template, redirect, url_for, Response
from app import wjl_app
from app.model import Field, Team, Session, Match, Sheet, WhichTeam
from app.errors import NotFoundException
from app.authentication import get_login_email, are_logged_in,\
    is_facebook_supported, is_github_supported, is_gmail_supported
import json


class WebsiteData(TypedDict):
    """Data that every website page needs."""
    logged_in: bool
    email: str


class TeamRecord(TypedDict):
    """A team record and stats"""
    id: int
    name: str
    wins: int
    losses: int
    games_played: int
    points_scored: int
    jams: int
    slots: int

    @staticmethod
    def empty_record(id: int, name: str):
        return {
            "id": id,
            "name": name,
            "wins": 0,
            "losses": 0,
            "games_played": 0,
            "points_scored": 0,
            "jams": 0,
            "slots": 0
        }


@wjl_app.route("/schedule")
def schedule():
    return render_template("schedule.html",
                           base_data=get_base_data())


@wjl_app.route("/standings")
def standings():
    league_sessions = [session.json() for session in Session.query.all()]
    return render_template("standings.html",
                           base_data=get_base_data(),
                           league_sessions=league_sessions)


@wjl_app.route("/standings/<int:session_id>")
def standing_table(session_id):
    session = Session.query.get(session_id)
    if session is None:
        return Response(None, status=404, mimetype="application/json")
    matches = Match.query.filter(Match.session_id == session_id).all()
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
                          key=lambda x: x["wins"] / min(1, x["games_played"]))
    print(team_records)
    return Response(json.dumps(team_records),
                    status=200, mimetype="application/json")


@wjl_app.route("/submit_score")
@login_required
def submit_score():
    """A route to submit a gamesheet for some match."""
    return render_template("submit_score.html",
                           base_data=get_base_data(),)


@wjl_app.route("/")
def homepage():
    """A route for the homepage."""
    return render_template("index.html",
                           base_data=get_base_data(),)


@wjl_app.route("/field/<int:field_id>")
@login_required
def field(field_id: int):
    """A route to view the given field."""
    field = Field.query.get(field_id)
    if field is None:
        raise NotFoundException("Sorry, field not found")
    return render_template("field.html",
                           field=field.json(),
                           base_data=get_base_data(),)


@wjl_app.route("/team/<int:team_id>")
@login_required
def team(team_id: int):
    """A route to view the given team."""
    team = Team.query.get(team_id)
    if team is None:
        raise NotFoundException("Sorry, field not found")
    return render_template("team.html",
                           team=team.json(),
                           base_data=get_base_data())


@wjl_app.route("/authenticate")
def need_to_login():
    """A route used to indicate the user needs to authenicate for some page."""
    return render_template("login.html",
                           message="Need to login to proceed further.",
                           base_data=get_base_data(),
                           github_enabled=is_github_supported(),
                           facebook_enabled=is_facebook_supported(),
                           gmail_enabled=is_gmail_supported())


@wjl_app.route("/login")
def loginpage():
    """A route to login the user."""
    return render_template("login.html",
                           base_data=get_base_data(),
                           github_enabled=is_github_supported(),
                           facebook_enabled=is_facebook_supported(),
                           gmail_enabled=is_gmail_supported())


@wjl_app.route("/logout")
@login_required
def logout():
    """A route to log out the user."""
    logout_user()
    print("You have logged out")
    return redirect(url_for("homepage"))


def get_base_data() -> WebsiteData:
    """Return base data needed for all pages.

    Returns:
        WebsiteData: the base website data needed to render the page
    """
    return {
        "logged_in": are_logged_in(),
        "email": get_login_email()
    }
