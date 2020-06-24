from app import wjl_app
from app.model import Field, Team
from app.authentication import requires_login, get_login_email, are_logged_in,\
    is_facebook_supported, is_github_supported, is_gmail_supported
from flask import render_template


@wjl_app.route("/schedule")
def schedule():
    return render_template("schedule.html",
                           logged_in=are_logged_in(),
                           email=get_login_email())


@wjl_app.route("/standings")
def standings():
    return render_template("standings.html",
                           logged_in=are_logged_in(),
                           email=get_login_email())


@wjl_app.route("/submit_score")
@requires_login
def submit_score():
    print(get_login_email())
    return render_template("submit_score.html",
                           logged_in=are_logged_in(),
                           email=get_login_email())


@wjl_app.route("/")
def homepage():
    return render_template("index.html",
                           logged_in=are_logged_in(),
                           email=get_login_email())


@wjl_app.route("/field/<int:field_id>")
@requires_login
def field(field_id: int):
    field = Field.query.get(field_id)
    if field is None:
        return render_template("error.html", message="Sorry field not found",
                               logged_in=are_logged_in(),
                               email=get_login_email())
    return render_template("field.html",
                           field=field.json(),
                           logged_in=are_logged_in(),
                           email=get_login_email())


@wjl_app.route("/team/<int:team_id>")
@requires_login
def team(team_id: int):
    team = Team.query.get(team_id)
    if team is None:
        return render_template("error.html", message="Sorry team not found",
                               logged_in=are_logged_in(),
                               email=get_login_email())
    return render_template("team.html",
                           team=team.json(),
                           logged_in=are_logged_in(),
                           email=get_login_email())


@wjl_app.route("/authenticate")
def need_to_login():
    return render_template("login.html",
                           message="Need to login to proceed further.",
                           logged_in=are_logged_in(),
                           email=get_login_email(),
                           github_enabled=is_github_supported(),
                           facebook_enabled=is_facebook_supported(),
                           gmail_enabled=is_gmail_supported())


@wjl_app.route("/login")
def loginpage():
    return render_template("login.html",
                           logged_in=are_logged_in(),
                           email=get_login_email(),
                           github_enabled=is_github_supported(),
                           facebook_enabled=is_facebook_supported(),
                           gmail_enabled=is_gmail_supported())
