from typing import TypedDict
from flask_login import logout_user, login_required
from flask import render_template, redirect, url_for, Response, request,\
    session
from flask_login import current_user
from sqlalchemy import func, asc, or_
from datetime import datetime
from app import wjl_app
from app.model import Field, Team, Session, Match, Sheet, WhichTeam,\
    DB, LeagueRequest, Player
from app.errors import NotFoundException, LackScorePermissionException,\
    OAuthException, NotConvenorException
from app.authentication import get_login_email, are_logged_in,\
    is_facebook_supported, is_github_supported, is_gmail_supported
from app.helpers import is_date_between_range, tomorrow_date
from app.logging import LOGGER
import json


class WebsiteData(TypedDict):
    """Data that every website page needs."""
    logged_in: bool
    email: str


class ScheduleRecord(TypedDict):
    """A schedule record"""
    id: int
    date: str
    home_team: str
    home_team_link: str
    away_team: str
    away_team_link: str
    field: str
    field_link: str
    result_link: str

    @staticmethod
    def create_schedule_record(match: Match) -> "ScheduleRecord":
        record = match.json()
        record["result_link"] = (url_for("match_result", match_id=match.id)
                                 if match.has_sheets() else None)
        record["home_team_link"] = url_for("team", team_id=match.home_team_id)
        record["away_team_link"] = url_for("team", team_id=match.away_team_id)
        record["field_link"] = url_for("field", field_id=match.field_id)
        return record


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
    def empty_record(team_id: int, team_name: str) -> "TeamRecord":
        return {
            "id": team_id,
            "name": team_name,
            "wins": 0,
            "losses": 0,
            "games_played": 0,
            "points_scored": 0,
            "jams": 0,
            "slots": 0,
            "team_link": url_for('team', team_id=team_id)
        }


class PendingRequest(TypedDict):
    team: str
    email: str
    name: str
    accept_link: str
    reject_link: str
    id: int

    @staticmethod
    def get_request(league_request: LeagueRequest) -> "PendingRequest":
        data = league_request.json()
        data["accept_link"] = url_for("league_request_decision",
                                      request_id=league_request.id,
                                      decision="accept")
        data["reject_link"] = url_for("league_request_decision",
                                      request_id=league_request.id,
                                      decision="reject")
        return data


@wjl_app.route("/schedule")
def schedule():
    league_sessions = [sesh.json() for sesh in Session.query.all()]
    active_session = get_active_session()
    active_session = (active_session
                      if active_session is not None
                      else league_sessions[-1])
    return render_template("schedule.html",
                           base_data=get_base_data(),
                           league_sessions=league_sessions,
                           active_session=active_session,
                           today=datetime.now().strftime("%Y-%m-%d"))


@wjl_app.route("/pending_requests")
@login_required
def check_league_requests():
    if not current_user.is_convenor:
        raise NotConvenorException("not a convenor")
    pending_requests = [PendingRequest.get_request(pending)
                        for pending in LeagueRequest.query.filter(
                            LeagueRequest.pending == True).all()]
    return render_template("league_requests.html",
                           base_data=get_base_data(),
                           pending_requests=pending_requests)


@wjl_app.route("/pending_requests/<int:request_id>/<decision>")
@login_required
def league_request_decision(request_id: int, decision: str):
    if not current_user.is_convenor:
        LOGGER.warning(
            f"{current_user} pretending to be a convenor")
        return Response(None, status=401, mimetype="application/json")
    league_request = LeagueRequest.query.get(request_id)
    if league_request is None:
        LOGGER.warning(
            f"{current_user} looking at league request {request_id} dne")
        return Response(None, status=404, mimetype="application/json")
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


@wjl_app.route("/schedule/<int:session_id>")
def schedule_table(session_id):
    sesh = Session.query.get(session_id)
    if sesh is None:
        LOGGER.warning(
            f"{current_user} looking at schedule session {session_id} dne")
        return Response(None, status=404, mimetype="application/json")
    matches = Match.query.filter(
        Match.session_id == session_id).order_by(asc(Match.date)).all()
    schedule = [ScheduleRecord.create_schedule_record(match)
                for match in matches]
    return Response(json.dumps(schedule),
                    status=200, mimetype="application/json")


@wjl_app.route("/standings")
def standings():
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
    sesh = Session.query.get(session_id)
    if sesh is None:
        LOGGER.warning(
            f"{current_user} looking at standings session {session_id} dne")
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
                          key=lambda x: x["wins"] / max(1, x["games_played"]))
    return Response(json.dumps(team_records),
                    status=200, mimetype="application/json")


@wjl_app.route("/match_results/<int:match_id>")
def match_result(match_id: int):
    match = Match.query.get(match_id)
    if match is None:
        raise NotFoundException(f"Sorry, match not found - {match_id}")
    sheets = [sheet.json() for sheet in match.sheets]
    return render_template("match_results.html",
                           base_data=get_base_data(),
                           match=match.json(),
                           sheets=sheets)


@wjl_app.route("/submit_score")
@login_required
def submit_score():
    """A route to get matches that one can submit scores for."""
    team_ids = [team.id for team in current_user.teams]
    all_matches = (Match.query
                   .filter(or_(Match.away_team_id.in_(team_ids),
                               Match.home_team_id.in_(team_ids)))
                   .filter(Match.date <= tomorrow_date())
                   .all())
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


@wjl_app.route("/match/<int:match_id>")
def match(match_id):
    match = Match.query.get(match_id)
    if match is None:
        LOGGER.warning(
            f"{current_user} tried accessing non-existent match {match_id}")
        return Response(None, status=404, mimetype="application/json")
    match_data = match.json()
    sheets = []
    for sheet in match.sheets:
        sheets.append(sheet.json())
    match_data["sheets"] = sheets
    return Response(json.dumps(match_data),
                    status=200, mimetype="application/json")


@wjl_app.route("/join_league", methods=["POST"])
def join_league():
    """A form submission to ask to join the league."""
    # ensure given an email
    email = session.get("oauth_email", None)
    if email is None:
        # it should have been stored after authenicating
        message = "Sorry, the authentication provider did not give an email"
        raise OAuthException(message)

    # ensure the selected team exists
    team_id = request.form.get("team", None)
    if team_id is None:
        raise NotFoundException(f"Team does not exist - {team_id}")
    team = Team.query.get(team_id)
    if team is None:
        raise NotFoundException(f"Team does not exist - {team_id}")

    # save the request
    league_request = LeagueRequest(email, request.form.get("name", None), team)
    DB.session.add(league_request)
    DB.session.commit()
    message = ("Submitted request to join."
               " Please wait until a convenor responds")
    return render_template("error.html",
                           base_data=get_base_data(),
                           message=message)


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


@wjl_app.route("/")
def homepage():
    """A route for the homepage."""
    next_page = session.get("next", None)
    if next_page is not None:
        # remove it so can return to homepage again
        session.pop("next")
        return redirect(next_page)
    return render_template("index.html",
                           base_data=get_base_data(),)


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
    LOGGER.info(f"{current_user} has logged out")
    logout_user()
    return redirect(url_for("homepage"))


@wjl_app.route("/privacy")
def privacy_policy():
    """A route for the privacy policy."""
    return render_template("privacy_policy.html", base_data=get_base_data())


@wjl_app.route("/terms-and-conditions")
def terms_and_conditions():
    """A route for the terms and conditions."""
    return render_template("terms_and_conditions.html",
                           base_data=get_base_data())


def get_base_data() -> WebsiteData:
    """Return base data needed for all pages.

    Returns:
        WebsiteData: the base website data needed to render the page
    """
    if are_logged_in():
        print(f"Convenor: {current_user.is_convenor}")
    return {
        "logged_in": are_logged_in(),
        "email": get_login_email(),
        "is_convenor": are_logged_in() and current_user.is_convenor
    }


def get_active_session() -> Session:
    """Get the active league session.

    Returns:
        Session: the current active session otherwise None
    """
    start_date = func.min(Match.date).label("session_start")
    end_date = func.max(Match.date).label("session_end")
    sessions = DB.session.query(start_date, end_date,
                                Match.session_id).group_by(Match.session_id)
    current = datetime.now()
    for sesh in sessions:
        if is_date_between_range(current, sesh[0], sesh[1]):
            LOGGER.debug(f"Active session is {sesh}")
            return Session.query.get(sesh[2])
    return None
