# -*- coding: utf-8 -*-
"""Holds videos page routes."""
from flask import render_template
from app import wjl_app
from app.views.helper import get_base_data


@wjl_app.route("/videos")
def videos():
    """A route for the league videos."""
    return render_template("videos.html", base_data=get_base_data())
