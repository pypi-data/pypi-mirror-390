from .public_model import (
    app as pm_app,
)
from .env import app as env_app

internal_apps = [
    pm_app,
    env_app,
]
