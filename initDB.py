from app import DB
from app.model import Field, Team
import json


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


DB.drop_all()
DB.create_all()
fields_lookup = add_fields("data/fields.json")
team_lookup = add_teams("data/teams.json", fields_lookup)
