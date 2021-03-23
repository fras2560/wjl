# -*- coding: utf-8 -*-
"""Holds a database model for the application."""
from typing import TypedDict
from enum import Enum
from datetime import datetime
from flask_login import UserMixin
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.exc import NoResultFound
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
    teams = DB.relationship('Team',
                            secondary=roster,
                            backref=DB.backref('playerteams',
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
            "name": self.name,
            "is_convenor": self.is_convenor
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

    @staticmethod
    def from_json(data) -> 'Player':
        player_id = data.get("id")
        if player_id is not None:
            player = Player.query.get(player_id)
            if player is None:
                raise NotFoundException(f"Player not found: {player_id}")
            player.name = data.get("name")
            player.email = data.get("email")
            player.is_convenor = data.get("is_convenor")
            return player
        return Player(data.get("email"),
                      name=data.get("name"),
                      is_convenor=data.get("is_convenor"))


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

    @staticmethod
    def from_name(name) -> 'Field':
        try:
            return Field.query.filter_by(name=name).one()
        except NoResultFound:
            return None

    @staticmethod
    def from_json(data) -> 'Field':
        field_id = data.get("id")
        if field_id is not None:
            field = Field.query.get(field_id)
            if field is None:
                raise NotFoundException(f"Field not found: {field_id}")
            field.name = data.get("name")
            field.description = data.get("description")
            field.link = data.get("link")
            return field
        return Field(data.get("name"),
                     description=data.get("description"),
                     link=data.get("link"))

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
                              backref=DB.backref('teamsplayers',
                                                 lazy='dynamic'))

    def __init__(self, name: str, home_field: Field = None):
        self.name = name
        self.home_field_id = None if home_field is None else home_field.id

    def json(self) -> dict:
        players = [player.json() for player in self.players]
        field = ("No homefield"
                 if self.home_field is None
                 else self.home_field.name)
        return {
            "id": self.id,
            "name": self.name,
            "players": players,
            "homefield": {
                "name": field,
                "id": None if self.home_field is None else self.home_field.id
            }
        }

    def add_player(self, player: Player) -> None:
        """Add the given player to the team"""
        if player is None:
            raise NotFoundException(
                f"Trying to add non-existent player to team - {self.id}")
        self.players.append(player)

    def remove_player(self, player: Player) -> None:
        """Add the given player to the team"""
        if player is None:
            raise NotFoundException(
                f"Trying to add non-existent player to team - {self.id}")
        self.players.remove(player)

    def __str__(self) -> str:
        return self.name

    @staticmethod
    def from_json(data) -> 'Team':
        team_id = data.get("id")
        if data.get('homefield') is not None:
            field = Field.from_json(data.get('homefield'))
        else:
            field = None
        if team_id is not None:
            team = Team.query.get(team_id)
            if team is None:
                raise NotFoundException(f"team not found: {team_id}")
            team.name = data.get("name")
            team.homefield = field
            team.players = []
            for player_info in data.get('players'):
                player = Player.from_json(player_info)
                team.add_player(player)
            return team
        team = Team(data.get("name"), home_field=field)
        for player_info in data.get('players'):
            player = Player.from_json(player_info)
            team.add_player(player)
        return team


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
    active = DB.Column(DB.Boolean)
    matches = DB.relationship('Match',
                              backref='matches', lazy='dynamic')

    def __init__(self, name: str, active: bool = True):
        self.name = name
        self.active = active

    def json(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "active": self.active
        }

    def __str__(self) -> str:
        return self.name

    @staticmethod
    def from_json(data) -> 'Session':
        session_id = data.get("id")
        if session_id is not None:
            sesh = Session.query.get(session_id)
            if sesh is None:
                raise NotFoundException(f"Session not found: {session_id}")
            sesh.name = data.get("name")
            sesh.active = data.get("active")
            return sesh
        return Session(data.get("name"), data.get("active", True))


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
        self.home_team_id = None if home_team is None else home_team.id
        self.away_team_id = None if away_team is None else away_team.id
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
            "field_id": self.field_id,
            "date": self.date.strftime("%Y-%m-%d"),
            "time": self.date.strftime("%H:%M"),
            "datetime": self.date.strftime("%Y-%m-%d %H:%M"),
            "session": str(self.session),
            "session_id": self.session_id,
            "id": self.id,
            "status": self.status
        }

    @staticmethod
    def find_given_team(team_id) -> Team:
        """Find the team associated with the given team_id if it not None"""
        if team_id is None:
            return None
        team = Team.query.get(team_id)
        if team is None:
            raise NotFoundException(f"Team not found - {team_id}")
        return team

    @staticmethod
    def from_json(data) -> "Match":
        # ensure if given a team it is exists
        home_team = Match.find_given_team(data.get("home_team_id"))
        away_team = Match.find_given_team(data.get("away_team_id"))

        # ensure the field exists
        field_id = data.get("field_id", None)
        field = None if field_id is None else Field.query.get(field_id)
        if field is None:
            raise NotFoundException(f"Field not found - {field_id}")

        # ensure the session exists
        sesh_id = data.get("session_id", None)
        sesh = None if sesh_id is None else Session.query.get(sesh_id)
        if sesh is None:
            raise NotFoundException(f"Session not found - {sesh_id}")

        # try parsing date
        raw_date = data.get("datetime")
        date = None
        try:
            date = datetime.strptime(raw_date, '%Y-%m-%d %H:%M')
        except ValueError:
            raise NotFoundException(f"Unable to handle date: {raw_date}")

        match_id = data.get("id", None)
        if match_id is not None:
            # updating an match
            match = Match.query.get(match_id)
            if match is None:
                raise NotFoundException(f"Match not found - {sesh_id}")
            match.date = date
            match.session_id = sesh.id
            match.status = data.get("status")
            match.away_team_id = None if away_team is None else away_team.id
            match.home_team_id = None if home_team is None else home_team.id
            match.field_id = field.id
            return match
        else:
            # creating a match
            return Match(home_team, away_team, sesh, date, field,
                         status=data.get("status"))

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
            "away_deuces": self.away_deuces,
            "id": self.id,
            "match_id": self.match_id
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
