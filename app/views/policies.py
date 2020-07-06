# -*- coding: utf-8 -*-
"""Holds privacy and terms policies."""
from flask import render_template
from app import wjl_app
from app.views.helper import get_base_data


@wjl_app.route("/privacy")
def privacy_policy():
    """A route for the privacy policy."""
    return render_template("privacy_policy.html", base_data=get_base_data())


@wjl_app.route("/terms-and-conditions")
def terms_and_conditions():
    """A route for the terms and conditions."""
    return render_template("terms_and_conditions.html",
                           base_data=get_base_data())
