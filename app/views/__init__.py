# -*- coding: utf-8 -*-
"""Holds all website the views."""
__all__ = []
from flask import session, redirect, render_template, send_from_directory
from app import wjl_app
from app.views.helper import get_base_data
import pkgutil
import inspect


@wjl_app.route("/robots.txt")
def robot():
    """A route for the google web crawler."""
    return send_from_directory(wjl_app.static_folder, "robots.txt")


@wjl_app.route("/")
def homepage():
    """A route for the homepage."""
    next_page = session.get("next", None)
    if next_page is not None:
        # remove it so can return to homepage again
        session.pop("next")
        return redirect(next_page)
    return render_template("index.html",
                           base_data=get_base_data(),)


@wjl_app.route("/wheel-spin")
def spin_wheel_page():
    """A route for the spinning wheel page."""
    return render_template("game_wheel.html", base_data=get_base_data())


for loader, name, is_pkg in pkgutil.walk_packages(__path__):
    module = loader.find_module(name).load_module(name)

    for name, value in inspect.getmembers(module):
        if name.startswith('__'):
            continue

        globals()[name] = value
        __all__.append(name)
