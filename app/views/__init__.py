# -*- coding: utf-8 -*-
"""Website views

Holds all website the views.
"""
__all__ = []
from flask import session, redirect, render_template
from app import wjl_app
from app.views.helper import get_base_data
import pkgutil
import inspect


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


for loader, name, is_pkg in pkgutil.walk_packages(__path__):
    module = loader.find_module(name).load_module(name)

    for name, value in inspect.getmembers(module):
        if name.startswith('__'):
            continue

        globals()[name] = value
        __all__.append(name)
