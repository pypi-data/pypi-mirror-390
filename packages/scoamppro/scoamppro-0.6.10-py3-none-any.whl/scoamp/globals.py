import os
import subprocess

from .api import AmpApi
from .utils.api_utils import (
    load_auth,
    DEFAULT_ENDPOINT,
)


SCOAMP_ENDPOINT = os.getenv("SCOAMP_ENDPOINT", DEFAULT_ENDPOINT)
SCOAMP_ACCESS_KEY = os.getenv("SCOAMP_ACCESS_KEY")
SCOAMP_SECRET_KEY = os.getenv("SCOAMP_SECRET_KEY")
SCOAMP_PATH_PREFIX = os.getenv("SCOAMP_PATH_PREFIX")
SCOAMP_AUTH_V1 = os.getenv("SCOAMP_AUTH_V1", True)


global_api = AmpApi()


def set_endpoint(ep: str) -> None:
    global_api.set_endpoint(ep)


def set_auth_info(access_key: str, secret_key: str) -> None:
    global_api.set_auth_info(access_key, secret_key)


def set_path_prefix(path_prefix: bool) -> None:
    global_api.set_path_prefix(path_prefix)


def set_auth_v1(auth_v1: bool) -> None:
    global_api.set_auth_v1(auth_v1)


# load auth from environment variables
if SCOAMP_ACCESS_KEY and SCOAMP_SECRET_KEY:
    set_endpoint(SCOAMP_ENDPOINT)
    set_auth_info(SCOAMP_ACCESS_KEY, SCOAMP_SECRET_KEY)
    set_path_prefix(SCOAMP_PATH_PREFIX)
    set_auth_v1(SCOAMP_AUTH_V1)
else:
    # try to load local cached auth info
    # TODO switch endpoint
    try:
        auth = load_auth()
        set_endpoint(auth.endpoint)
        set_auth_info(auth.access_key, auth.secret_key)
        set_path_prefix(auth.path_prefix)
        set_auth_v1(auth.auth_v1)
    except Exception:
        ...


class Environment:
    git_version = ""  # 'None' means not installed
    lfs_version = ""  # 'None' means not installed

    @classmethod
    def check_git_and_lfs(cls):
        """
        Checks that `git` and `git-lfs` can be run.

        Raises:
            - [`EnvironmentError`](https://docs.python.org/3/library/exceptions.html#EnvironmentError)
              if `git` or `git-lfs` are not installed.
        """
        try:
            if cls.git_version is None:
                # cached result
                raise FileNotFoundError
            elif cls.git_version:
                pass
            else:
                cls.git_version = subprocess.run(
                    ["git", "--version"],
                    stderr=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    encoding="utf-8",
                    check=True,
                ).stdout.strip()
        except FileNotFoundError:
            cls.git_version = None
            raise EnvironmentError(
                "Looks like you do not have git installed, please install."
            )

        try:
            if cls.lfs_version is None:
                # cached result
                raise FileNotFoundError
            elif cls.lfs_version:
                pass
            else:
                cls.lfs_version = subprocess.run(
                    ["git-lfs", "--version"],
                    stderr=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    encoding="utf-8",
                    check=True,
                ).stdout.strip()
        except FileNotFoundError:
            cls.lfs_version = None
            raise EnvironmentError(
                "Looks like you do not have git-lfs installed, please install."
                " You can install from https://git-lfs.github.com/."
                " Then run `git lfs install` (you only have to do this once)."
            )

        return cls.git_version + "\n" + cls.lfs_version
