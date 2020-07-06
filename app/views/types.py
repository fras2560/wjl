# -*- coding: utf-8 -*-
"""Holds the various types that form interface between front-end & back-end"""
from typing import TypedDict
from flask import url_for
from app.model import Match, LeagueRequest


class WebsiteData(TypedDict):
    """Data that every website page needs."""
    logged_in: bool
    email: str


class ScheduleRecord(TypedDict):
    """A schedule record"""
    id: int
    date: str
    home_team: str
    home_team_link: str
    away_team: str
    away_team_link: str
    field: str
    field_link: str
    result_link: str
    status: str

    @staticmethod
    def create_schedule_record(match: Match) -> "ScheduleRecord":
        """Create a schedule record for the given match."""
        record = match.json()
        record["result_link"] = (url_for("match_result", match_id=match.id)
                                 if match.has_sheets() else None)
        record["home_team_link"] = (None
                                    if match.home_team_id is None
                                    else url_for("team",
                                                 team_id=match.home_team_id))
        record["away_team_link"] = (None
                                    if match.away_team_id is None
                                    else url_for("team",
                                                 team_id=match.away_team_id))
        record["field_link"] = url_for("field", field_id=match.field_id)
        return record


class TeamRecord(TypedDict):
    """A team record and stats"""
    id: int
    name: str
    wins: int
    losses: int
    games_played: int
    points_scored: int
    jams: int
    slots: int

    @staticmethod
    def empty_record(team_id: int, team_name: str) -> "TeamRecord":
        """Generate an empty record for the given team."""
        return {
            "id": team_id,
            "name": team_name,
            "wins": 0,
            "losses": 0,
            "games_played": 0,
            "points_scored": 0,
            "jams": 0,
            "slots": 0,
            "team_link": url_for('team', team_id=team_id)
        }


class PendingRequest(TypedDict):
    """A pending request to join the league."""
    team: str
    email: str
    name: str
    accept_link: str
    reject_link: str
    id: int

    @staticmethod
    def get_request(league_request: LeagueRequest) -> "PendingRequest":
        """Generates a pending request from a league request."""
        data = league_request.json()
        data["accept_link"] = url_for("league_request_decision",
                                      request_id=league_request.id,
                                      decision="accept")
        data["reject_link"] = url_for("league_request_decision",
                                      request_id=league_request.id,
                                      decision="reject")
        return data
