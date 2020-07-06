from flask import Response, render_template
from flask_login import current_user
from sqlalchemy import asc
from app import wjl_app
from app.model import Session, Match
from app.views.helper import get_active_session, get_base_data
from app.views.types import ScheduleRecord
from app.logging import LOGGER
from datetime import datetime
import json


@wjl_app.route("/schedule/<int:session_id>")
def schedule_table(session_id):
    sesh = Session.query.get(session_id)
    if sesh is None:
        LOGGER.warning(
            f"{current_user} looking at schedule session {session_id} dne")
        return Response(None, status=404, mimetype="application/json")
    matches = Match.query.filter(
        Match.session_id == session_id).order_by(asc(Match.date)).all()
    schedule = [ScheduleRecord.create_schedule_record(match)
                for match in matches]
    return Response(json.dumps(schedule),
                    status=200, mimetype="application/json")


@wjl_app.route("/schedule")
def schedule():
    league_sessions = [sesh.json() for sesh in Session.query.all()]
    active_session = get_active_session()
    active_session = (active_session
                      if active_session is not None
                      else league_sessions[-1])
    return render_template("schedule.html",
                           base_data=get_base_data(),
                           league_sessions=league_sessions,
                           active_session=active_session,
                           today=datetime.now().strftime("%Y-%m-%d"))
