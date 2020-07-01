
from flask import render_template, session, url_for, redirect
from flask_login import current_user
from app import wjl_app
from app.errors import OAuthException, NotFoundException,\
    NotPartOfLeagueException, HaveLeagueRequestException,\
    NotConvenorException
from app.model import Team, LeagueRequest
from app.views import get_base_data
from app.logging import LOGGER
import traceback


@wjl_app.route("/existing_league_request")
def handle_existing_league_request():
    is_pending = LeagueRequest.query.filter(
        LeagueRequest.email == session["oauth_email"]).one()
    return render_template("pending_league_request.html",
                           base_data=get_base_data(),
                           is_pending=is_pending.pending)


@wjl_app.route("/want_to_join")
def handle_not_part_of_league():
    teams = [team.json() for team in Team.query.all()]
    return render_template("not_part_of_league.html",
                           base_data=get_base_data(),
                           teams=teams)


@wjl_app.route("/something_went_wrong")
def handle_generic_error():
    """Handle generic errors"""
    message = str(session.pop("runtimeException",
                              "Sorry, something went wrong"))
    LOGGER.warning(f"{current_user}: {message}")
    return render_template("error.html",
                           base_data=get_base_data(),
                           message=message)


@wjl_app.errorhandler(NotFoundException)
@wjl_app.errorhandler(OAuthException)
@wjl_app.errorhandler(NotConvenorException)
@wjl_app.errorhandler(NotPartOfLeagueException)
@wjl_app.errorhandler(HaveLeagueRequestException)
@wjl_app.errorhandler(Exception)
def error_request_director(error):
    """Redirect all errors to their handler to prevent double submits"""
    if isinstance(error, NotPartOfLeagueException):
        return redirect(url_for("handle_not_part_of_league"))
    elif isinstance(error, HaveLeagueRequestException):
        return redirect(url_for("handle_existing_league_request"))
    elif (isinstance(error, NotFoundException) or
            isinstance(error, NotConvenorException) or
            isinstance(error, OAuthException)):
        session["runtimeException"] = str(error)
        return redirect(url_for("handle_generic_error"))
    else:
        # probably should look into this
        LOGGER.error("Unhandled exception")
        LOGGER.error(error)
        traceback.print_exc()
        return redirect(url_for("handle_generic_error"))
