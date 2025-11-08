"""GFA application."""

# Due to typer usage:

from __future__ import annotations

import typer

from .ops import app as ops_app
from .views import app as views_app

APP = typer.Typer(rich_markup_mode="rich")


APP.add_typer(views_app.APP, name="view")
ops_app.add_applications(APP)
