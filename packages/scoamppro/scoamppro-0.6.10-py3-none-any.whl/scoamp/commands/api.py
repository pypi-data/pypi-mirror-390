import json
import typer
from typing import Optional, List
from rich import print
from rich.table import Table

from ..globals import (
    global_api,
    set_auth_info,
    set_endpoint,
)
from ..api import AmpApi
from ..toolkit import (
    snapshot_download,
    create_and_upload_model,
    API_FILE_DOWNLOAD_PARALLEL_PART_SIZE,
    API_FILE_DOWNLOAD_READ_CHUNK_SIZE,
    API_FILE_DOWNLOAD_ACCELERATE,
    MiB,
    API_FILE_DOWNLOAD_MAX_RETRY_NUMBERS,
    API_FILE_DOWNLOAD_CONNECT_TIMEOUT,
    API_FILE_DOWNLOAD_READ_TIMEOUT,
)
from ..utils.api_utils import (
    ApiEnv,
    save_auth,
    load_auth,
    PAGE_MAX,
)
from ..utils.helper import format_datetime
from ..utils.error import (
    NotLoginError,
    err_wrapper,
)

app = typer.Typer(name="api")


@app.command(help="login user")
def login(
    access_key: Optional[str] = typer.Option(None, "-ak", "--access-key"),
    secret_key: Optional[str] = typer.Option(None, "-sk", "--secret-key"),
    env: ApiEnv = typer.Option(
        ApiEnv.standard.value,
        metavar=f"[{ApiEnv.standard.value}|{ApiEnv.custom.value}]",
        help="login server, use 'custom' to specify your arbitrary address",
    ),
    path_prefix: bool = typer.Option(
        True,
        "--path-prefix/--no-path-prefix",
        help="Enable or disable path prefix (default: enabled)",
    ),
    auth_v1: bool = typer.Option(
        True,
        "--auth-v1/--auth-v2",
        help="Use sensecore 1.0 auth or 2.0 auth (default: 1.0)",
    ),
):
    # parameter validation
    env_name, endpoint = env.value, env.endpoint()
    if env is ApiEnv.custom:
        env_name = typer.prompt("Env name")

    # check already exists auth
    auth_info = None
    try:
        auth_info = load_auth(env_name)
    except NotLoginError:
        pass
    else:
        if env is ApiEnv.custom:
            flag = typer.confirm(
                f"Found already logined env '{auth_info.endpoint}', use it?"
            )
            if flag:
                endpoint = auth_info.endpoint
            else:
                auth_info = None

    if not endpoint:
        endpoint = typer.prompt("Env endpoint")
    print(f"Environment ({env_name}): {endpoint}")

    if auth_info and not access_key:
        flag = typer.confirm(
            f"Found already logined access key '{auth_info.access_key}', use it?"
        )
        if flag:
            access_key = auth_info.access_key
            secret_key = auth_info.secret_key

    # normal
    if not access_key:
        access_key = typer.prompt("Input access key")
    if not secret_key:
        secret_key = typer.prompt("Input secret key", hide_input=True)

    # auth validation
    api = AmpApi(access_key, secret_key, endpoint, path_prefix, auth_v1=auth_v1)
    _ = api.get_user_info()

    # cache auth
    save_auth(env_name, endpoint, access_key, secret_key, path_prefix, auth_v1)

    print("Login Succeed!")


@app.command(help="list user's models")
@err_wrapper
def list(
    n: int = typer.Option(
        -1, "-n", "--num", min=-1, max=PAGE_MAX, help="max record numbers, '-1' for all"
    ),
    s: Optional[str] = typer.Option(
        None, "-s", "--search", help="fuzzy search keyword for model name"
    ),
    simple: bool = typer.Option(False, help="simple json formatted output"),
):
    # make request
    jr = global_api.list_user_models(n, s)
    if not jr:
        print("Nothing returned.")
        raise typer.Exit(0)

    # parse response and print result
    models, page = jr["models"], jr["page"]
    count, total = page["size"], page["total"]
    res = []
    for m in models:
        meta = m["metadata"]
        tags = meta["tags"]
        tags.extend(
            filter(
                lambda x: x,
                (
                    meta["training_frameworks"],
                    meta["type"],
                    meta["algorithm"],
                    meta["industry"],
                ),
            )
        )
        res.append(
            {
                "display_name": m["display_name"],
                "name": m["name"],
                "repository_uri": m["repository_uri"],
                "owner_name": m["owner_name"],
                "tags": tags,
                "create_time": m["create_time"],
                "update_time": m["update_time"],
            }
        )

    if simple:
        print(json.dumps(res, indent=2))
    else:
        table = Table(
            title=f"Model Information({count}/{total})", show_lines=True, show_edge=True
        )
        for header in ("Name", "ID", "URL", "Owner", "Tags", "Created", "Updated"):
            table.add_column(header, style="cyan", overflow="fold")
        for r in res:
            table.add_row(
                r["display_name"],
                r["name"],
                r["repository_uri"],
                r["owner_name"],
                ",".join(r["tags"]),
                format_datetime(r["create_time"]),
                format_datetime(r["update_time"]),
            )

        print(table)


@app.command(help="download user or public model")
@err_wrapper
def get(
    model_id: str = typer.Argument(..., help="model id/name"),
    local_dir: str = typer.Option(
        None, "-d", "--local-dir", help="local target directory"
    ),
    is_public: bool = typer.Option(
        False,
        "-pub",
        "--is-public",
        is_flag=True,
        help="whether public model, or private user model",
    ),
    zone: str = typer.Option(
        None, "-z", "--zone", help="zone of model replicate, e.g. cn-sh-01p"
    ),
    revision: str = typer.Option(
        None, "-rev", "--revision", help="git commit/branch/tag"
    ),
    force_download: bool = typer.Option(
        False,
        "-f",
        "--force",
        is_flag=True,
        help="force download exists file in local_dir",
    ),
    ignore_patterns: List[str] = typer.Option(
        None,
        "-igp",
        "--ignore-patterns",
        help="ignore files of which name match patterns, support multiple values",
    ),
    parallels: int = typer.Option(
        4, "-j", "--parallels", min=1, help="parallels of downloading"
    ),
    access_key: Optional[str] = typer.Option(
        None, "-ak", "--access-key", help="access key"
    ),
    secret_key: Optional[str] = typer.Option(
        None, "-sk", "--secret-key", help="secret key"
    ),
    endpoint: Optional[str] = typer.Option(
        None,
        "-ep",
        "--endpoint",
        help="amp endpoint, values can be from 'standard' for simple, or other url format string, e.g. https://example.com",
    ),
    verbose: bool = typer.Option(
        False, "-v", "--verbose", is_flag=True, help="verbose log"
    ),
    part_size: int = typer.Option(
        API_FILE_DOWNLOAD_PARALLEL_PART_SIZE / MiB,
        "-ps",
        "--part-size",
        min=1,
        help="part-size(MB) of downloading",
    ),
    chunk_size: int = typer.Option(
        API_FILE_DOWNLOAD_READ_CHUNK_SIZE / MiB,
        "-cs",
        "--chunk-size",
        min=1,
        help="chunk-size(MB) of downloading",
    ),
    acc: bool = typer.Option(
        API_FILE_DOWNLOAD_ACCELERATE,
        "-acc",
        "--accelerate",
        is_flag=True,
        help="use accelerate extension",
    ),
    max_retry_num: int = typer.Option(
        API_FILE_DOWNLOAD_MAX_RETRY_NUMBERS,
        "-try",
        "--try",
        min=1,
        help=f"max numbers of try download file's range-part, default {API_FILE_DOWNLOAD_MAX_RETRY_NUMBERS}",
    ),
    connect_timeout: int = typer.Option(
        API_FILE_DOWNLOAD_CONNECT_TIMEOUT,
        "-ct",
        "--connect-timeout",
        min=1,
        help=f"connect timeout when download file's range-part, {API_FILE_DOWNLOAD_CONNECT_TIMEOUT}",
    ),
    read_timeout: int = typer.Option(
        API_FILE_DOWNLOAD_READ_TIMEOUT,
        "-rt",
        "--read-timeout",
        min=1,
        help=f"read timeout when download file's range-part, {API_FILE_DOWNLOAD_READ_TIMEOUT}",
    ),
) -> None:
    if verbose:
        import logging
        from ..utils.logger import get_logger

        logger = get_logger()
        logger.setLevel(logging.DEBUG)

    _config_global_api(access_key, secret_key, endpoint)

    if not local_dir:
        local_dir = model_id

    part_size = part_size * MiB
    chunk_size = chunk_size * MiB
    r = snapshot_download(
        model_id=model_id,
        local_dir=local_dir,
        is_public=is_public,
        zone=zone,
        revision=revision,
        force_download=force_download,
        ignore_patterns=ignore_patterns,
        parallels=parallels,
        part_size=part_size,
        chunk_size=chunk_size,
        acc=acc,
        max_retry_num=max_retry_num,
        connect_timeout=connect_timeout,
        read_timeout=read_timeout,
    )
    print(f"download successfully: {r}")


@app.command(help="create and upload user model")
@err_wrapper
def create(
    model_id: str = typer.Argument(..., help="model id/name"),
    local_dir: str = typer.Option(
        ..., "-d", "--local-dir", help="local model directory"
    ),
    model_space: str = typer.Option(
        ..., "-ms", "--mode-space", help="AMP model space id"
    ),
    access_key: Optional[str] = typer.Option(
        None, "-ak", "--access-key", help="access key"
    ),
    secret_key: Optional[str] = typer.Option(
        None, "-sk", "--secret-key", help="secret key"
    ),
    endpoint: Optional[str] = typer.Option(
        None,
        "-ep",
        "--endpoint",
        help="amp endpoint, values can be from 'standard' for simple, or other url format string, e.g. https://example.com",
    ),
):
    _config_global_api(access_key, secret_key, endpoint)

    r = create_and_upload_model(
        model_id=model_id,
        local_dir=local_dir,
        model_space_name=model_space,
        allow_exist=True,
    )
    print(f"create model successfully: {r}")


@app.command(help="command stub", hidden=True)
@err_wrapper
def stub(): ...


def _config_global_api(access_key, secret_key, endpoint):
    if access_key or secret_key:
        if not access_key or not secret_key:
            raise ValueError("'access_key' and 'secret_key' both should be given")
        set_auth_info(access_key, secret_key)

    if endpoint:
        try:
            endpoint = ApiEnv(endpoint).endpoint()
        except ValueError:
            ...
        set_endpoint(endpoint)
