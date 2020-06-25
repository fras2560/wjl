from typing import TypedDict
from enum import Enum
from datetime import datetime
from flask_login import UserMixin
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from flask_sqlalchemy import SQLAlchemy

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
    SCORE = "SCORE"
    SLOT = "SLOT"
    DINGERS = "DINGERS"
    JAMS = "JAMS"
    DEUCES = "DEUCES"

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
    """
    id = DB.Column(DB.Integer, primary_key=True)
    email = DB.Column(DB.String(256), unique=True)
    name = DB.Column(DB.String(256))

    def __init__(self, email: str, name: str = None):
        self.email = email
        self.name = name

    def json(self) -> dict:
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name
        }


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


class Team(DB.Model):
    """
        A class used to store the team information
        Columns:
            name: the name of the team

    """
    id = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String(120), unique=True)
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


class Session(DB.Model):
    """
        A session is a collection of games
        Columns:
            name: the name of the session
    """
    id = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String(120))

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
    session_id = DB.Column(DB.Integer, DB.ForeignKey("session.id"))
    session = DB.relationship(Session)
    date = DB.Column(DB.DateTime)
    status = DB.Column(DB.String(120))

    def __init__(self, home_team: Team, away_team: Team, session: Session,
                 date: datetime, status: str = None):
        self.home_team_id = home_team.id
        self.away_team_id = away_team.id
        self.session_id = session.id
        self.date = date
        self.status = status


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
    away_dingers = DB.Column(DB.Integer)
    away_deuces = DB.Column(DB.Integer)
    away_jams = DB.Column(DB.Integer)

    def __init__(self, match: Match,
                 home_sheet: TeamSheet, away_sheet: TeamSheet):
        self.match_id = match.id
        self.home_score = home_sheet.get(TeamSheet.SCORE)
        self.home_slot = home_sheet.get(TeamSheet.SLOT)
        self.home_dingers = home_sheet.get(TeamSheet.DINGERS)
        self.home_deuces = home_sheet.get(TeamSheet.DEUCES)
        self.home_jams = home_sheet.get(TeamSheet.JAMS)
        self.away_score = away_sheet.get(TeamSheet.SCORE)
        self.away_slot = away_sheet.get(TeamSheet.SLOT)
        self.away_dingers = away_sheet.get(TeamSheet.DINGERS)
        self.away_deuces = away_sheet.get(TeamSheet.DEUCES)
        self.away_jams = away_sheet.get(TeamSheet.JAMS)

    def who_won(self) -> WhichTeam:
        """Return who won the given sheet."""
        if self.home_slot:
            return WhichTeam.HOME_TEAM
        elif self.away_slot:
            return WhichTeam.HOME_TEAM
        elif self.home_score > self.away_score:
            return WhichTeam.HOME_TEAM
        elif self.home_score < self.away_score:
            return WhichTeam.AWAY_TEAM
        return WhichTeam.TIE

    def was_ot(self) -> bool:
        """Returns whether the game went into overtime."""
        return (self.home_score > STANDARD_SCORE_LIMIT or
                self.away_score > STANDARD_SCORE_LIMIT)
