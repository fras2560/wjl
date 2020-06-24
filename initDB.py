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


def add_teams(field_lookup: dict) -> dict:
    """Add the teams to the database."""
    # add the teams
    team_lookup = {}
    teams = [("Dallas Cowboys", "Queen's Mary"),
             ("The Disc Heads", ""),
             ("Deaner Dunglers", "Deaner's Park"),
             ("Frisbeers", ""),
             ("Pavy Petunias", ""),
             ("Bluevale bullies!", "Hudson's Home"),
             ("Wiener Jammers", "Weinsteins"),
             ("Space Jam", "Tucker's Palace"),
             ("Harvaяd Cossacks", "Harvaяd")]
    for team in teams:
        temp = Team(team[0],
                    home_field=field_lookup.get(team[1], None))
        DB.session.add(temp)
        DB.session.commit()
        team_lookup[team[0]] = temp


DB.drop_all()
DB.create_all()
fields_lookup = add_fields("fields.json")
team_lookup = add_teams(fields_lookup)
