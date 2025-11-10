import io
import os
import requests
import threading
from functools import lru_cache
from contextlib import AbstractContextManager
from typing import BinaryIO
from datetime import datetime, timezone, timedelta


class SliceFileObj(AbstractContextManager):
    """
    Utility context manager to read a *slice* of a seekable file-like object as a seekable, file-like object.

    This is NOT thread safe

    Inspired by stackoverflow.com/a/29838711/593036

    Credits to @julien-c

    Args:
        fileobj (`BinaryIO`):
            A file-like object to slice. MUST implement `tell()` and `seek()` (and `read()` of course).
            `fileobj` will be reset to its original position when exiting the context manager.
        seek_from (`int`):
            The start of the slice (offset from position 0 in bytes).
        read_limit (`int`):
            The maximum number of bytes to read from the slice.

    Attributes:
        previous_position (`int`):
            The previous position

    Examples:

    Reading 200 bytes with an offset of 128 bytes from a file (ie bytes 128 to 327):
    ```python
    >>> with open("path/to/file", "rb") as file:
    ...     with SliceFileObj(file, seek_from=128, read_limit=200) as fslice:
    ...         fslice.read(...)
    ```

    Reading a file in chunks of 512 bytes
    ```python
    >>> import os
    >>> chunk_size = 512
    >>> file_size = os.getsize("path/to/file")
    >>> with open("path/to/file", "rb") as file:
    ...     for chunk_idx in range(ceil(file_size / chunk_size)):
    ...         with SliceFileObj(file, seek_from=chunk_idx * chunk_size, read_limit=chunk_size) as fslice:
    ...             chunk = fslice.read(...)

    ```
    """

    def __init__(self, fileobj: BinaryIO, seek_from: int, read_limit: int):
        self.fileobj = fileobj
        self.seek_from = seek_from
        self.read_limit = read_limit

    def __enter__(self):
        self._previous_position = self.fileobj.tell()
        is_eos = self.fileobj.seek(0, os.SEEK_END)
        self._len = min(self.read_limit, is_eos - self.seek_from)
        # ^^ The actual number of bytes that can be read from the slice
        self.fileobj.seek(self.seek_from, io.SEEK_SET)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.fileobj.seek(self._previous_position, io.SEEK_SET)

    def read(self, n: int = -1):
        pos = self.tell()
        if pos >= self._len:
            return b""
        remaining_amount = self._len - pos
        data = self.fileobj.read(
            remaining_amount if n < 0 else min(n, remaining_amount)
        )
        return data

    def tell(self) -> int:
        return self.fileobj.tell() - self.seek_from

    def seek(self, offset: int, whence: int = os.SEEK_SET) -> int:
        start = self.seek_from
        end = start + self._len
        if whence in (os.SEEK_SET, os.SEEK_END):
            offset = start + offset if whence == os.SEEK_SET else end + offset
            offset = max(start, min(offset, end))
            whence = os.SEEK_SET
        elif whence == os.SEEK_CUR:
            cur_pos = self.fileobj.tell()
            offset = max(start - cur_pos, min(offset, end - cur_pos))
        else:
            raise ValueError(f"whence value {whence} is not supported")
        return self.fileobj.seek(offset, whence) - self.seek_from

    def __iter__(self):
        yield self.read(n=4 * 1024 * 1024)


def get_session() -> requests.Session:
    """
    Get a `requests.Session` object, using configuration from the user.

    Use [`get_session`] to get a configured Session. Since `requests.Session` is not guaranteed to be thread-safe,
    this function creates 1 Session instance per thread. A LRU cache is used to cache the created sessions (and connections) between calls.
    Max size is 128 to avoid memory leaks if thousands of threads are spawned.

    See [this issue](https://github.com/psf/requests/issues/2766) to know more about thread-safety in `requests`.

    Example:
    ```py
    session = get_session().get("https://example.com")
    ```
    """
    return _get_session_from_cache(thread_ident=threading.get_ident())


@lru_cache(
    maxsize=128
)  # default value for Python>=3.8. Let's keep the same for Python3.7
def _get_session_from_cache(thread_ident: int) -> requests.Session:
    """
    Create a new session per thread using global parameters. Using LRU cache (maxsize 128) to avoid memory leaks when
    using thousands of threads.
    """
    return requests.Session()


def format_datetime(time_str: str):
    dt = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
    beijing_tz = timezone(timedelta(hours=8))
    beijing_dt = dt.astimezone(beijing_tz)
    return beijing_dt.strftime("%Y-%m-%d %H:%M:%S")


def str_to_int(raw):
    if not raw:
        return 0

    try:
        return int(raw)
    except ValueError:
        return humanreadable_str_to_int(raw)


def humanreadable_str_to_int(raw):
    raw = raw.lower()
    units = ("", "k", "m", "g", "t", "p", "e")
    num, unit = float(raw[:-1]), raw[-1]
    idx = units.index(unit)
    factor = 1000**idx
    return int(num * factor)
