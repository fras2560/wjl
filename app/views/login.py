# -*- coding: utf-8 -*-
"""Holds views related to login and authenticating"""
from flask import render_template, redirect, url_for, request, session
from flask_login import current_user, logout_user, login_required,\
    login_user
from app import wjl_app
from app.authentication import is_facebook_supported, is_github_supported,\
    is_gmail_supported
from app.model import LeagueRequest, OAuth, Team, Player, DB
from app.logging import LOGGER
from app.views.helper import get_base_data
from app.errors import OAuthException, NotFoundException,\
    HaveLeagueRequestException


@wjl_app.route("/delete-account")
def delete_account_page():
    """A route used to delete the user account."""
    LOGGER.info(f"{current_user} is considering deleting their account")
    return render_template("delete_account.html",
                           base_data=get_base_data())


@wjl_app.route("/delete-user", methods=["POST"])
def delete_account():
    """A post request that deletes the current user."""
    LOGGER.info(f"{current_user} is deleting their account")
    current_user.teams = []
    DB.session.commit()
    OAuth.query.filter_by(player_id=current_user.id).delete()
    DB.session.delete(current_user)
    DB.session.commit()
    logout_user()
    return redirect(url_for("homepage"))


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


@wjl_app.route("/join_league", methods=["POST"])
def join_league():
    """A form submission to ask to join the league."""
    # ensure given an email
    email = session.get("oauth_email", None)
    if email is None:
        # it should have been stored after authenicating
        message = "Sorry, the authentication provider did not give an email"
        raise OAuthException(message)
    # double check the player email has not be taken
    player = Player.query.filter(Player.email == email).first()
    if player is not None:
        login_user(player)
        return redirect(url_for("homepage"))
    # double check this is not  refresh page issue
    pending_request = LeagueRequest.query.filter(
        LeagueRequest.email == email).first()
    if pending_request is not None:
        raise HaveLeagueRequestException("Double submit on form")
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
    return redirect(url_for("league_request_sent"))


@wjl_app.route("/request_sent", methods=["GET"])
def league_request_sent():
    message = ("Submitted request to join."
               " Please wait until a convenor responds")
    return render_template("error.html",
                           base_data=get_base_data(),
                           message=message)
