
from flask import render_template, session
from flask_login import current_user
from app import wjl_app
from app.errors import OAuthException, NotFoundException,\
    NotPartOfLeagueException, HaveLeagueRequestException,\
    NotConvenorException
from app.model import Team, LeagueRequest
from app.views import get_base_data
from app.logging import LOGGER


@wjl_app.errorhandler(HaveLeagueRequestException)
def handle_existing_league_request(error):
    is_pending = LeagueRequest.query.filter(
        LeagueRequest.email == session["oauth_email"]).one()
    return render_template("pending_league_request.html",
                           base_data=get_base_data(),
                           is_pending=is_pending.pending)


@wjl_app.errorhandler(NotPartOfLeagueException)
def hangle_not_part_of_league(error):
    teams = [team.json() for team in Team.query.all()]
    return render_template("not_part_of_league.html",
                           base_data=get_base_data(),
                           teams=teams)


@wjl_app.errorhandler(NotFoundException)
@wjl_app.errorhandler(OAuthException)
@wjl_app.errorhandler(NotConvenorException)
def handle_generic_error(error):
    message = str(error)
    LOGGER.warning(f"{current_user}: {message}")
    return render_template("error.html",
                           base_data=get_base_data(),
                           message=message)
