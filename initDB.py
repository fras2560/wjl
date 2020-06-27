from datetime import datetime
from app import wjl_app
from app.model import Field, Team, DB, Match, Session, Sheet, TeamSheet
import json
import csv


def add_fields(file_path: str) -> dict:
    """Adds the fields that are in the json file"""
    fields = {}
    # loads the field data from a json file
    with open(file_path, "r") as f:
        fields = json.load(f)

    field_lookup = {}
    for name, info in fields.items():
        # add the fields
        temp = Field(name,
                     description=info["description"],
                     link=info["link"])
        DB.session.add(temp)
        DB.session.commit()
        field_lookup[name] = temp
    return field_lookup


def add_teams(file_path: str, field_lookup: dict) -> dict:
    """Add the teams to the database."""
    team_lookup = {}
    teams = {}
    # loads the team data from a json file
    with open(file_path, "r") as f:
        teams = json.load(f)
    for name, info in teams.items():
        temp = Team(name,
                    home_field=field_lookup.get(info["homefield"], None))
        DB.session.add(temp)
        DB.session.commit()
        team_lookup[name] = temp
    return team_lookup


def add_session() -> Session:
    """Add the session to the database."""
    sesh = Session("Summer 2020")
    DB.session.add(sesh)
    DB.session.commit()
    return sesh


def add_matches(file_path: str, session: Session, field_lookup: dict,
                team_lookup: dict) -> dict:
    """Add the matches to the database."""
    match_lookup = {}
    matches = {}
    with open(file_path, "r") as f:
        matches = json.load(f)
    for match in matches:
        home_team = team_lookup[match["home_team"].strip()]
        away_team = team_lookup[match["away_team"].strip()]
        field = field_lookup[match["field"].strip()]
        date = datetime.strptime(match["date"].strip(), '%Y-%m-%d %H:%M')
        temp = Match(home_team, away_team, session, date, field)
        DB.session.add(temp)
        DB.session.commit()
        match_lookup[home_team.name + away_team.name] = temp
    return match_lookup


def parse_int(value: str) -> int:
    try:
        return int(value)
    except Exception:
        return 0


def create_teamsheet(home_team: bool, sheet: dict) -> TeamSheet:
    """Returns a team sheet from the sheet"""
    prefix = "Home" if home_team else "Away"
    teamsheet = TeamSheet.empty_sheet()
    teamsheet[TeamSheet.SCORE] = parse_int(sheet[f"{prefix} Score"])
    teamsheet[TeamSheet.SLOT] = (True
                                 if parse_int(sheet[f"{prefix} Slots"]) >= 1
                                 else False)
    teamsheet[TeamSheet.JAMS] = parse_int(sheet[f"{prefix} Jams"])
    return teamsheet


def add_sheets(file_path: str, match_lookup) -> None:
    """Add the sheets to the database."""
    with open(file_path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for sheet in csv_reader:
            homesheet = create_teamsheet(True, sheet)
            awaysheet = create_teamsheet(False, sheet)
            match = match_lookup[sheet['Home Team'].strip() +
                                 sheet['Away Team'].strip()]
            temp = Sheet(match, homesheet, awaysheet)
            DB.session.add(temp)
            DB.session.commit()


with wjl_app.app_context():
    DB.drop_all()
    DB.create_all()
    field_lookup = add_fields("data/fields.json")
    team_lookup = add_teams("data/teams.json", field_lookup)
    session = add_session()
    match_lookup = add_matches("data/matches.json", session,
                               field_lookup, team_lookup)
    add_sheets("data/sheets.csv", match_lookup)
