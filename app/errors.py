# -*- coding: utf-8 -*-
"""Holds exceptions for the application."""


class OAuthException(Exception):
    """An exception while dealing with oauth provider."""
    pass


class NotPartOfLeagueException(Exception):
    """An exception while dealing with oauth provider."""
    pass


class NotFoundException(Exception):
    """An exception occurred when looking for some model entity."""
    pass


class LackScorePermissionException(Exception):
    """An exception when trying to submit score for team not part of."""
    pass


class HaveLeagueRequestException(Exception):
    """When a player is  authenticating but have a rejected/pending request."""
    pass


class NotConvenorException(Exception):
    """When a player is trying to be a convenor."""
    pass
