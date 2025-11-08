from __future__ import annotations

import contextlib
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .get_db_connection import get_db_connection
from .get_ssh_connection import get_ssh_connection

if TYPE_CHECKING:
    from collections.abc import Generator


@contextlib.contextmanager
def remote_connect(
    *,
    ssh_config_path: Path,
    my_cnf_path: Path,
    my_cnf_connection_name: str,
    db_name: str,
) -> Generator[Any, Any, None]:
    """Connect to mysql via ssh tunnel."""
    with (
        get_ssh_connection(ssh_config_path) as local_bind_port,
        get_db_connection(
            my_cnf_path,
            local_bind_port=local_bind_port,
            connection_name=my_cnf_connection_name,
            db_name=db_name,
        ) as db_conn,
    ):
        yield db_conn
