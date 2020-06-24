from app import DB
from app.model import Player
from functools import wraps
from sqlalchemy import func
from flask import render_template, redirect, url_for
from flask_dance.contrib.github import github
from flask_dance.contrib.facebook import facebook
from flask_dance.contrib.google import google


def requires_login(fnc):
    """A decorator to use for views the require a user to be logged in"""
    @wraps(fnc)
    def decorated(*args, **kwargs):
        print("running login check")
        if not are_logged_in():
            return redirect(url_for("need_to_login"))
        email = get_login_email()
        if email is None:
            return render_template(
                "error.html",
                message="Sorry, not sure you part of the league.")
        players = DB.session.query(Player).filter(
            func.lower(Player.email) == email.lower()).all()
        if len(players) == 0:
            return render_template(
                "error.html",
                message="Sorry, not sure you part of the league.")
        return fnc(*args, **kwargs)
    return decorated


def are_logged_in() -> bool:
    """Returns whether the person is logged in."""
    return github.authorized or google.authorized or facebook.authorized


def get_login_email() -> str:
    """Returns the email based whichever app they have authorized with."""
    if github.authorized:
        resp = github.get("user")
        assert resp.ok
        return resp.json().get("email", None)
    elif facebook.authorized:
        resp = facebook.get("/me")
        assert resp.ok, resp.text
        return resp.json().get("email", None)
    elif google.authorized:
        resp = google.get("/oauth2/v1/userinfo")
        assert resp.ok, resp.text
        return resp.json().get("email", None)
