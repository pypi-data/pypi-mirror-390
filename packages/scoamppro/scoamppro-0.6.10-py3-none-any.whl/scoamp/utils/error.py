from enum import Enum
from functools import wraps
import typer
from jsonschema import ValidationError
from requests import HTTPError, Response

from .logger import get_logger


class ScoampBaseError(Exception):
    pass


class NotLoginError(ScoampBaseError):
    pass


class APIError(ScoampBaseError):
    def __init__(self, resp, *args):
        msg = f"Call AMP API Error(status={resp.status_code}, url={resp.url}):\n{resp.content.decode('utf-8')}"
        super().__init__(msg, *args)
        self.status_code = resp.status_code
        self.url = resp.url


class FileFormatError(ScoampBaseError):
    pass


class SubprocessError(ScoampBaseError):
    pass


class FileDownloadError(ScoampBaseError):
    pass


class OutOfMaxRetryNumbersError(ScoampBaseError):
    pass


class UnKnownError(ScoampBaseError):
    pass


class ExitCode(int, Enum):
    DefaultError = 127
    LoginError = 1
    ApiError = 2
    MetaInvalidError = 3


def err_wrapper(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        logger = get_logger()

        def _print_err_func(desc, exc=None):
            if kwargs.get("verbose"):
                logger.exception(desc)
            else:
                if exc:
                    desc = str(exc)
                logger.error(desc)

        try:
            return f(*args, **kwargs)
        except NotLoginError:
            _print_err_func("no or invalid auth info, use 'scoamp login' first")
            raise typer.Exit(ExitCode.LoginError)
        except APIError as exc:
            _print_err_func("call amp api error", exc)
            raise typer.Exit(ExitCode.ApiError)
        except (FileFormatError, ValidationError):
            _print_err_func("invalid file format")
            raise typer.Exit(ExitCode.MetaInvalidError)
        except typer.Exit:
            raise
        except Exception as exc:
            _print_err_func(f"something wrong: {str(exc)}")
            raise typer.Exit(ExitCode.DefaultError)

    return wrapper


def amp_raise_for_status(response: Response):
    try:
        response.raise_for_status()
    except HTTPError as exc:
        raise APIError(response) from exc
