import json
import sys
import subprocess
import threading
import typer
import concurrent.futures as futures
from pathlib import Path
from typing import Dict, List, Optional

from ..utils.helper import (
    SliceFileObj,
    get_session,
)


TRANSFER_NAME = "amp-multipart"

app = typer.Typer(
    name="lfs", help="lfs extension for large files uploading, no need to login"
)


@app.command()
def setup(
    repo_path: Path = typer.Argument(
        ..., exists=True, file_okay=False, resolve_path=True
    ),
):
    subprocess.run(
        ["git", "config", f"lfs.customtransfer.{TRANSFER_NAME}.path", "scoamp"],
        check=True,
        cwd=repo_path,
    )
    subprocess.run(
        ["git", "config", f"lfs.customtransfer.{TRANSFER_NAME}.args", "lfs upload"],
        check=True,
        cwd=repo_path,
    )
    subprocess.run(
        ["git", "config", f"lfs.customtransfer.{TRANSFER_NAME}.concurrent", "false"],
        check=True,
        cwd=repo_path,
    )
    print("Successfully set up scoamp lfs custom transfer for large files!")


@app.command(hidden=True)
def upload():
    # Immediately after invoking a custom transfer process, git-lfs
    # sends initiation data to the process over stdin.
    # This tells the process useful information about the configuration.
    init_msg = read_msg(check=False)
    if not (init_msg.get("event") == "init" and init_msg.get("operation") == "upload"):
        write_msg({"error": {"code": 32, "message": "Wrong lfs init operation"}})
        sys.exit(1)

    ref_concurrency = max(init_msg.get("concurrenttransfers", 4), 1)

    # The transfer process should use the information it needs from the
    # initiation structure, and also perform any one-off setup tasks it
    # needs to do. It should then respond on stdout with a simple empty
    # confirmation structure, as follows:
    write_msg({})

    # After the initiation exchange, git-lfs will send any number of
    # transfer requests to the stdin of the transfer process, in a serial sequence.
    while True:
        msg = read_msg()
        if msg is None:
            # When all transfers have been processed, git-lfs will send
            # a terminate event to the stdin of the transfer process.
            # On receiving this message the transfer process should
            # clean up and terminate. No response is expected.
            sys.exit(0)

        oid = msg["oid"]
        filepath = msg["path"]
        completion_url = msg["action"]["href"]
        header: Dict = msg["action"]["header"]
        chunk_size = int(header.pop("chunk_size"))
        auth = header.pop("Authorization", None)

        # parse presigned urls of parts from action header in ascend order
        # e.g.
        #   {"00001": "https://path1", "00002": "https://path2", ...}
        klist = []
        for k in header:
            try:
                kid = int(k)
            except ValueError:
                continue

            klist.append((kid, k))
        klist = sorted(klist, key=lambda t: t[0])
        presigned_urls: List[str] = [header[i[1]] for i in klist]

        # Send a "started" progress event to allow other workers to start.
        # Otherwise they're delayed until first "progress" event is reported,
        # i.e. after the first 5GB by default (!)
        write_msg(
            {
                "event": "progress",
                "oid": oid,
                "bytesSoFar": 1,
                "bytesSinceLast": 0,
            }
        )

        # caculate workload per thread
        n_url = len(presigned_urls)
        n_thread = min(n_url, ref_concurrency)
        n_heavy = n_url % n_thread
        # n_light = n_thread - n_heavy
        n_per_light_thread = n_url // n_thread
        n_per_heavy_thread = n_per_light_thread + 1

        parts = []
        n_processed_bytes = 0
        lock = threading.Lock()
        err = False

        def _thread_process(start, n):
            nonlocal parts, n_processed_bytes, lock, err

            # open file for each thread
            with open(filepath, "rb") as file:
                for i in range(start, start + n):
                    # cancel running if error occurred
                    if err:
                        return
                    presigned_url = presigned_urls[i]
                    with SliceFileObj(
                        file,
                        seek_from=i * chunk_size,
                        read_limit=chunk_size,
                    ) as data:
                        r = get_session().put(presigned_url, data=data)
                        r.raise_for_status()

                        n_bytes = data.tell()
                        with lock:
                            parts.append(
                                {
                                    "etag": r.headers.get("etag"),
                                    "partNumber": i + 1,
                                }
                            )
                            n_processed_bytes += n_bytes

                            # the transfer process should post messages to stdout
                            write_msg(
                                {
                                    "event": "progress",
                                    "oid": oid,
                                    "bytesSoFar": n_processed_bytes,
                                    "bytesSinceLast": n_bytes,
                                }
                            )

        tasks = []
        executor = futures.ThreadPoolExecutor(max_workers=n_thread)
        for i in range(n_thread):
            if i < n_heavy:
                # prcoess more chunk
                n = n_per_heavy_thread
                start = i * n_per_heavy_thread
            else:
                # process less chunk
                n = n_per_light_thread
                start = (
                    n_heavy * n_per_heavy_thread + (i - n_heavy) * n_per_light_thread
                )

            tasks.append(executor.submit(_thread_process, start, n))

        # wait for first exception or all completed
        done, _ = futures.wait(tasks, return_when=futures.FIRST_EXCEPTION)

        # raise from failed task
        try:
            for task in done:
                task.result()
        except Exception as exc:
            # set err flag to notice running futures to terminate immediatly
            err = True
            executor.shutdown(wait=False)
            write_msg(
                {
                    "event": "complete",
                    "oid": oid,
                    "error": {"code": 2, "message": str(exc)},
                }
            )
            raise exc
        else:
            executor.shutdown(wait=True)

        # call complete url
        parts = sorted(parts, key=lambda part: part["partNumber"])
        headers = {"Authorization": auth} if auth else None
        r = get_session().post(
            completion_url,
            json={
                "oid": oid,
                "parts": parts,
            },
            headers=headers,
        )
        r.raise_for_status()

        write_msg({"event": "complete", "oid": oid})


def write_msg(msg: Dict):
    """Write out the message in Line delimited JSON."""
    msg_str = json.dumps(msg) + "\n"
    sys.stdout.write(msg_str)
    sys.stdout.flush()


def read_msg(check: bool = True) -> Optional[Dict]:
    """Read Line delimited JSON from stdin."""
    msg = json.loads(sys.stdin.readline().strip())
    if not check:
        return msg

    if "terminate" in (msg.get("type"), msg.get("event")):
        # terminate message received
        return None

    if msg.get("event") not in ("download", "upload"):
        sys.exit(1)

    return msg
