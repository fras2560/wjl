
from flask import render_template
from flask_login import current_user
from app import wjl_app
from app.errors import OAuthException, NotFoundException,\
    NotPartOfLeagueException
from app.views import get_base_data
from app.logging import LOGGER


@wjl_app.errorhandler(NotFoundException)
@wjl_app.errorhandler(OAuthException)
@wjl_app.errorhandler(NotPartOfLeagueException)
def handle_generic_error(error):
    message = str(error)
    LOGGER.warning(f"{current_user}: {message}")
    return render_template("error.html",
                           base_data=get_base_data(),
                           message=message)
