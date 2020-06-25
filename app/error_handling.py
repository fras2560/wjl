
from flask import render_template
from app import wjl_app
from app.authentication import are_logged_in, get_login_email
from app.errors import OAuthException, NotFoundException,\
    NotPartOfLeagueException


@wjl_app.errorhandler(NotFoundException)
@wjl_app.errorhandler(OAuthException)
@wjl_app.errorhandler(NotPartOfLeagueException)
def handle_generic_error(error):
    message = str(error)
    return render_template("error.html",
                           message=str(message),
                           logged_in=are_logged_in(),
                           email=get_login_email())
