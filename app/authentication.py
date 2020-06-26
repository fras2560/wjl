from typing import TypedDict
from flask import Blueprint
from flask_dance.contrib.github import make_github_blueprint
from flask_dance.contrib.facebook import make_facebook_blueprint
from flask_dance.contrib.google import make_google_blueprint
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from flask_dance.consumer import oauth_authorized, oauth_error
from flask_login import LoginManager, current_user, login_user
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import func
from app.errors import OAuthException, NotPartOfLeagueException
from app.model import DB, Player, OAuth
import os


login_manager = LoginManager()
login_manager.login_view = "loginpage"

github_blueprint = make_github_blueprint(
    scope=["email"],
    storage=SQLAlchemyStorage(OAuth, DB.session, user=current_user)
)
facebook_blueprint = make_facebook_blueprint(
    scope=["email"],
    storage=SQLAlchemyStorage(OAuth, DB.session, user=current_user))
google_blueprint = make_google_blueprint(
    scope=["profile", "email"],
    storage=SQLAlchemyStorage(OAuth, DB.session, user=current_user))
FACEBOOK = "facebook"
GOOGLE = "google"
GITHUB = "github"


class UserInfo(TypedDict):
    """The user info from a ouath provider"""
    name: str
    email: str


@oauth_authorized.connect_via(facebook_blueprint)
@oauth_authorized.connect_via(github_blueprint)
@oauth_authorized.connect_via(google_blueprint)
def oauth_service_provider_logged_in(blueprint: Blueprint, token: str):
    # ensure the token is correct
    if not token:
        raise OAuthException("Failed to log in")

    # get the user info
    user_info = get_user_info(blueprint)
    user_id = user_info["id"]

    # user user info to lookup oauth
    oauth = get_oauth(blueprint.name, user_id, token)
    if oauth.player:
        login_user(oauth.player)
        print("Successfully signed in.")
    else:
        # see if they part of the legaue
        player = find_player(user_info)
        # associated the player with this oauth
        oauth.player = player
        DB.session.add(oauth)
        DB.session.commit()
        print("Successfully signed in.")
    # Disable Flask-Dance's default behavior for saving the OAuth token
    return False


@oauth_error.connect_via(facebook_blueprint)
def oauth_service_provider_error(blueprint, message: str, response):
    msg = f"{blueprint.name}! message={message} response={response}"
    raise OAuthException(msg)


@login_manager.user_loader
def load_user(player_id: int) -> Player:
    return Player.query.get(int(player_id))


def get_oauth(name: str, user_id: str, token: str) -> OAuth:
    """Get the oauth associated with the given user id and oauth provider.

    Args:
        name (str): the name of the oauth provider
        user_id (str): the id of the user according to oauth provider
        token (str): the oauth token

    Returns:
        OAuth: the oauth that we have saved or newly created one
    """
    # Find this OAuth token in the database, or create it
    user_id = str(user_id)
    query = OAuth.query.filter_by(provider=name, provider_user_id=user_id)
    try:
        oauth = query.one()
    except NoResultFound:
        oauth = OAuth(provider=name, provider_user_id=user_id, token=token)
    return oauth


def get_user_info(blueprint: Blueprint) -> UserInfo:
    """Get the user info from the oauth provider.

    Args:
        blueprint (Blueprint): the oauth provider blueprint

    Raises:
        OAuthException: Unsupported blueprint or unable to get user info

    Returns:
        UserInfo: the user info
    """
    resp = None
    if blueprint.name == FACEBOOK:
        resp = blueprint.session.get("/me")
    elif blueprint.name == GOOGLE:
        resp = blueprint.session.get("/oauth2/v1/userinfo")
    elif blueprint.name == GITHUB:
        resp = blueprint.session.get("user")
    if resp is None:
        raise OAuthException(f"Unsupported oauth blueprint: {blueprint.name}")
    if not resp.ok:
        raise OAuthException(
            f"Failed to get user info oauth blueprint: {blueprint.name}")
    return resp.json()


def find_player(user_info: UserInfo) -> Player:
    """Find the player associated with the user info.

    Args:
        user_info (UserInfo): the user info

    Raises:
        NotPartOfLeagueException: if the user not part of league

    Returns:
        Player: the player in the legaue
    """
    email = user_info.get('email')
    players = DB.session.query(Player).filter(
        func.lower(Player.email) == email.lower()).all()
    if len(players) == 0:
        raise NotPartOfLeagueException(
            "Sorry, looks like you are not in the league")
    return players[0]


def are_logged_in() -> bool:
    """Returns whether the person is logged in."""
    return current_user.get_id() is not None


def get_login_email() -> str:
    """Returns the email based whichever app they have authorized with."""
    return None if not are_logged_in() else current_user.email


def is_gmail_supported() -> bool:
    """Returns whether current setup support Gmail authentication."""
    return os.environ.get("GOOGLE_OAUTH_CLIENT_ID", "") != ""


def is_github_supported() -> bool:
    """Returns whether current setup support Github authentication."""
    return os.environ.get("GITHUB_OAUTH_CLIENT_ID", "") != ""


def is_facebook_supported() -> bool:
    """Returns whether current setup support Facebook authentication."""
    return os.environ.get("FACEBOOK_OAUTH_CLIENT_ID", "") != ""
