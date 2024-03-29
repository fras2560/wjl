# -*- coding: utf-8 -*-
"""Holds helper functions for other views."""
from flask_login import current_user
from datetime import datetime
from sqlalchemy import func
from app import wjl_app
from app.views.types import WebsiteData
from app.authentication import are_logged_in, get_login_email
from app.helpers import is_date_between_range
from app.model import Match, Session, DB
from app.logging import LOGGER


def get_base_data() -> WebsiteData:
    """Return base data needed for all pages.

    Returns:
        WebsiteData: the base website data needed to render the page
    """
    return {
        "logged_in": are_logged_in(),
        "email": get_login_email(),
        "is_convenor": are_logged_in() and current_user.is_convenor,
        "testing": wjl_app.config['ARE_TESTING']
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


def get_some_session() -> Session:
    """Get some league session.

    Returns:
        Session: the current active session otherwise just some session
    """
    sess = get_active_session()
    sess = sess if sess is not None else Session.query.filter(Session.active == True).first()
    return sess if sess is not None else Session.query.first()


def get_session_default_empty(sessions) -> Session:
    """Get a session from list of sessions but if empty return empty session"""
    if len(sessions) >= 1:
        return sessions[-1]
    return Session("no sessions").json()
