from typing import TypedDict
from enum import Enum
from datetime import datetime
from flask_login import UserMixin
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from flask_sqlalchemy import SQLAlchemy
from app.errors import NotFoundException

""" The score limit of a standard game."""
STANDARD_SCORE_LIMIT = 21
"""The database object."""
DB = SQLAlchemy()


class TeamSheet(TypedDict):
    """A team sheet for a game"""
    score: int
    slot: bool
    dingers: int
    deuces: int
    jams: int
    SCORE = "score"
    SLOT = "slot"
    DINGERS = "dingers"
    JAMS = "jams"
    DEUCES = "deuces"

    @staticmethod
    def empty_sheet() -> 'TeamSheet':
        """Returns an empty team sheet"""
        return {
            TeamSheet.SCORE: 0,
            TeamSheet.SLOT: False,
            TeamSheet.DINGERS: 0,
            TeamSheet.DEUCES: 0,
            TeamSheet.JAMS: 0
        }

    @staticmethod
    def from_json(sheet: dict, team: 'WhichTeam') -> 'TeamSheet':
        """Returns an empty team sheet"""
        if team == WhichTeam.HOME_TEAM:
            return {
                TeamSheet.SCORE: sheet.get("home_score"),
                TeamSheet.SLOT: sheet.get("home_slot"),
                TeamSheet.DINGERS: sheet.get("home_dingers"),
                TeamSheet.DEUCES: sheet.get("home_deuces"),
                TeamSheet.JAMS: sheet.get("home_jams")
            }
        else:
            return {
                TeamSheet.SCORE: sheet.get("away_score"),
                TeamSheet.SLOT: sheet.get("away_slot"),
                TeamSheet.DINGERS: sheet.get("away_dingers"),
                TeamSheet.DEUCES: sheet.get("away_deuces"),
                TeamSheet.JAMS: sheet.get("away_jams")
            }


class WhichTeam(Enum):
    """Which team won the game."""
    HOME_TEAM = "hometeam"
    AWAY_TEAM = "awayteam"
    TIE = "tie"


roster = DB.Table('roster',
                  DB.Column('player_id',
                            DB.Integer,
                            DB.ForeignKey('player.id')),
                  DB.Column('team_id', DB.Integer, DB.ForeignKey('team.id'))
                  )


class Player(UserMixin, DB.Model):
    """
        A class used to store the user information
        Columns:
            id: the unique id
            email: the email associated with the user
            name: the name of the player
            convenor: whether has convenor privileges
            submit_scores: whether able to submit scores
    """
    id = DB.Column(DB.Integer, primary_key=True)
    email = DB.Column(DB.String(256), unique=True)
    name = DB.Column(DB.String(256))
    players = DB.relationship('Team',
                              secondary=roster,
                              backref=DB.backref('teamsplayers',
                                                 lazy='dynamic'))
    is_convenor = DB.Column(DB.Boolean)
    submit_scores = DB.Column(DB.Boolean)

    def __init__(self, email: str, name: str = None, is_convenor: bool = False,
                 submit_scores: bool = True):
        self.email = email
        self.name = name
        self.is_convenor = is_convenor
        self.submit_scores = submit_scores

    def json(self) -> dict:
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name
        }

    def __str__(self):
        return self.name

    def can_submit_scores(self, match: 'Match') -> bool:
        """Tells whether the player can submit scores for the given match."""
        if self.is_convenor:
            # convenor can submit scores for anyone
            return True
        elif not self.submit_scores:
            # submitting scores has been revoked due to abuse
            return False
        else:
            # check if they are part of team
            team_ids = [team.id for team in self.teams]
            return (match.away_team_id in team_ids or
                    match.home_team_id in team_ids)


class OAuth(OAuthConsumerMixin, DB.Model):
    provider_user_id = DB.Column(DB.String(256), unique=True, nullable=False)
    player_id = DB.Column(DB.Integer, DB.ForeignKey(Player.id), nullable=False)
    player = DB.relationship(Player)


class Field(DB.Model):
    """
        A class used to store the Field information
        Columns:
            name: the name of the team
            description: a description of the field
            link: a link usually to Google to where to find the field
    """
    id = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String(120), unique=True)
    description = DB.Column(DB.Text())
    link = DB.Column(DB.Text())

    def __init__(self, name: str,
                 description: str = None, link: str = None):
        self.name = name
        self.description = description
        self.link = link

    def json(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "link": self.link
        }

    def __str__(self) -> str:
        return self.name


class Team(DB.Model):
    """
        A class used to store the team information
        Columns:
            name: the name of the team

    """
    id = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String(120), unique=True, nullable=False)
    home_field_id = DB.Column(DB.Integer, DB.ForeignKey('field.id'))
    home_field = DB.relationship(Field)
    players = DB.relationship('Player',
                              secondary=roster,
                              backref=DB.backref('teams', lazy='dynamic'))

    def __init__(self, name: str, home_field: Field = None):
        self.name = name
        self.home_field_id = None if home_field is None else home_field.id

    def json(self) -> dict:
        players = [player.json() for player in self.players]
        field = ("No homefield"
                 if self.home_field is None
                 else self.home_field)
        return {
            "id": self.id,
            "name": self.name,
            "players": players,
            "homefield": field
        }

    def add_player(self, player: Player) -> None:
        """Add the given player to the team"""
        if player is None:
            raise NotFoundException(
                f"Trying to add non-existent player to team - {self.id}")
        self.players.append(player)

    def __str__(self) -> str:
        return self.name


class LeagueRequest(DB.Model):
    """
        A class used to store requests to join the league.
        Columns:
            team_id: the team they want to join
            name: the name they want to use
            email: the email from the Oauth provider
            pending: whether waiting for the outcome of the request
    """
    id = DB.Column(DB.Integer, primary_key=True)
    team_id = DB.Column(DB.Integer, DB.ForeignKey(Team.id), nullable=False)
    team = DB.relationship(Team)
    email = DB.Column(DB.String(120), unique=True, nullable=False)
    name = DB.Column(DB.String(120), nullable=False)
    pending = DB.Column(DB.Boolean)

    def __init__(self, email: str, name: str, team: Team):
        self.email = email
        self.name = name
        if team is None:
            raise NotFoundException("Given team does not exist")
        self.team_id = team.id
        self.pending = True

    def decline_request(self):
        self.pending = False

    def json(self):
        return {
            "team": self.team.json(),
            "email": self.email,
            "id": self.id,
            "pending": self.pending,
            "name": self.name
        }


class Session(DB.Model):
    """
        A session is a collection of games
        Columns:
            name: the name of the session
    """
    id = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String(120), unique=True)
    matches = DB.relationship('Match',
                              backref='matches', lazy='dynamic')

    def __init__(self, name: str):
        self.name = name

    def json(self) -> dict:
        return {
            "id": self.id,
            "name": self.name
        }


class Match(DB.Model):
    """
        A class used to store a match between two teams
        Columns:
            away_team_id: the id of the away team
            home_team_id: the id of the home team
            date: the date of the game
            status: the status of the game

    """
    id = DB.Column(DB.Integer, primary_key=True)
    away_team_id = DB.Column(DB.Integer, DB.ForeignKey("team.id"))
    away_team = DB.relationship(Team, foreign_keys=[away_team_id])
    home_team_id = DB.Column(DB.Integer, DB.ForeignKey("team.id"))
    home_team = DB.relationship(Team, foreign_keys=[home_team_id])
    field_id = DB.Column(DB.Integer, DB.ForeignKey("field.id"))
    field = DB.relationship(Field)
    session_id = DB.Column(DB.Integer, DB.ForeignKey("session.id"))
    session = DB.relationship(Session)
    sheets = DB.relationship('Sheet',
                             backref='sheets', lazy='dynamic')
    date = DB.Column(DB.DateTime)
    status = DB.Column(DB.String(120))

    def __init__(self, home_team: Team, away_team: Team, session: Session,
                 date: datetime, field: Field, status: str = None):
        self.home_team_id = home_team.id
        self.away_team_id = away_team.id
        self.session_id = session.id
        self.date = date
        self.status = status
        self.field_id = field.id

    def json(self) -> dict:
        home_team = "TBD" if self.home_team is None else self.home_team.name
        away_team = "TBD" if self.away_team is None else self.away_team.name
        field = "???" if self.field is None else self.field.name
        return {
            "home_team": home_team,
            "home_team_id": self.home_team_id,
            "away_team": away_team,
            "away_team_id": self.away_team_id,
            "field": field,
            "date": self.date.strftime("%Y-%m-%d"),
            "time": self.date.strftime("%H:%M"),
            "datetime": self.date.strftime("%Y-%m-%d %H:%M"),
            "id": self.id
        }

    def has_sheets(self) -> bool:
        for sheet in self.sheets:
            return True
        return False


class Sheet(DB.Model):
    """
        A class the holds a gamesheet for one game that part of a match.
    """
    id = DB.Column(DB.Integer, primary_key=True)
    match_id = DB.Column(DB.Integer, DB.ForeignKey("match.id"))
    match = DB.relationship(Match)
    home_score = DB.Column(DB.Integer)
    home_slot = DB.Column(DB.Boolean)
    home_dingers = DB.Column(DB.Integer)
    home_deuces = DB.Column(DB.Integer)
    home_jams = DB.Column(DB.Integer)
    away_score = DB.Column(DB.Integer)
    away_slot = DB.Column(DB.Boolean)
    away_dingers = DB.Column(DB.Integer)
    away_deuces = DB.Column(DB.Integer)
    away_jams = DB.Column(DB.Integer)

    def __init__(self, match: Match,
                 home_sheet: TeamSheet, away_sheet: TeamSheet):
        self.match_id = match.id
        self.set_awaysheet(away_sheet)
        self.set_homesheet(home_sheet)

    @staticmethod
    def from_json(sheet) -> 'Sheet':
        if "id" in sheet.keys() and sheet["id"] is not None:
            # load the original sheet and updates it values
            original_sheet = Sheet.query.get(sheet["id"])
            home_sheet = TeamSheet.from_json(sheet, WhichTeam.HOME_TEAM)
            away_sheet = TeamSheet.from_json(sheet, WhichTeam.AWAY_TEAM)
            original_sheet.set_awaysheet(away_sheet)
            original_sheet.set_homesheet(home_sheet)
            match_id = sheet.get("match_id")
            match = Match.query.get(match_id)
            if match is None:
                raise NotFoundException(f"Unable to find match: {match_id}")
            original_sheet.match_id = match_id
            return original_sheet
        else:
            home_sheet = TeamSheet.from_json(sheet, WhichTeam.HOME_TEAM)
            away_sheet = TeamSheet.from_json(sheet, WhichTeam.AWAY_TEAM)
            match_id = sheet.get("match_id")
            match = Match.query.get(match_id)
            if match is None:
                raise NotFoundException(f"Unable to find match: {match_id}")
            return Sheet(match, home_sheet, away_sheet)

    def json(self) -> dict:
        return {
            "home_score": self.home_score,
            "home_slot": self.home_slot,
            "home_jams": self.home_jams,
            "home_dingers": self.home_dingers,
            "home_deuces": self.home_deuces,
            "away_score": self.away_score,
            "away_slot": self.away_slot,
            "away_jams": self.away_jams,
            "away_dingers": self.away_dingers,
            "away_deuces": self.away_deuces
        }

    def set_homesheet(self, sheet: TeamSheet) -> None:
        self.home_score = sheet.get(TeamSheet.SCORE)
        self.home_slot = sheet.get(TeamSheet.SLOT)
        self.home_dingers = sheet.get(TeamSheet.DINGERS)
        self.home_deuces = sheet.get(TeamSheet.DEUCES)
        self.home_jams = sheet.get(TeamSheet.JAMS)

    def set_awaysheet(self, sheet: TeamSheet) -> None:
        self.away_score = sheet.get(TeamSheet.SCORE)
        self.away_slot = sheet.get(TeamSheet.SLOT)
        self.away_dingers = sheet.get(TeamSheet.DINGERS)
        self.away_deuces = sheet.get(TeamSheet.DEUCES)
        self.away_jams = sheet.get(TeamSheet.JAMS)

    def who_won(self) -> WhichTeam:
        """Return who won the given sheet."""
        if self.home_slot:
            return WhichTeam.HOME_TEAM
        elif self.away_slot:
            return WhichTeam.AWAY_TEAM
        elif self.home_score > self.away_score:
            return WhichTeam.HOME_TEAM
        elif self.home_score < self.away_score:
            return WhichTeam.AWAY_TEAM
        return WhichTeam.TIE

    def was_ot(self) -> bool:
        """Returns whether the game went into overtime."""
        return (self.home_score > STANDARD_SCORE_LIMIT or
                self.away_score > STANDARD_SCORE_LIMIT)
