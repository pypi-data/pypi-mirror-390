"""Operation applications."""

import typer

from .fix import app as fix_app
from .std import app as std_app
from .sub import app as sub_app


def add_applications(app: typer.Typer) -> None:
    """Add applications."""
    app.add_typer(fix_app.APP, name="fix")
    app.add_typer(std_app.APP, name="std")
    app.add_typer(sub_app.APP, name="sub")
