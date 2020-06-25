
from flask import render_template
from app import wjl_app
from app.errors import OAuthException, NotFoundException,\
    NotPartOfLeagueException
from app.views import get_base_data


@wjl_app.errorhandler(NotFoundException)
@wjl_app.errorhandler(OAuthException)
@wjl_app.errorhandler(NotPartOfLeagueException)
def handle_generic_error(error):
    message = str(error)
    return render_template("error.html",
                           base_data=get_base_data(),
                           message=str(message))
