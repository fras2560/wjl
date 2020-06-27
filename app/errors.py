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
