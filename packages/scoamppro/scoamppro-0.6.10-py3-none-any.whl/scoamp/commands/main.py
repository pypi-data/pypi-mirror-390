# from .. import __version__
from .api import app as api_app
from .lfs import app as lfs_app

# set api_app as main app
app = api_app

# add lfs extension
app.add_typer(lfs_app)

# try to import internal module
try:
    from .internal import internal_apps

    for iapp in internal_apps:
        app.add_typer(iapp)
except ModuleNotFoundError:
    ...


@app.command("version", help="version info")
def version():
    from ..version import version

    print(version)
