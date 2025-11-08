from __future__ import annotations

import configparser
import contextlib
import sys
from pathlib import Path
from urllib.parse import quote_plus

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


@contextlib.contextmanager
def get_db_connection(
    my_cnf_path: Path,
    *,
    local_bind_port: int,
    connection_name: str,
    db_name: str,
):
    """Connect to mysql via tunnel"""

    my_cnf_path = Path(my_cnf_path).expanduser()
    if not my_cnf_path.exists():
        raise FileNotFoundError(f"my.cnf file not found at {my_cnf_path}.")

    config_file = Path(my_cnf_path)
    config = configparser.ConfigParser()
    config.read(config_file)

    db_user = config[connection_name]["user"]
    db_password = config[connection_name]["password"]
    db_host = config[connection_name]["host"]

    db_password = quote_plus(db_password)

    sys.stdout.write(f"DB:  Connecting as {db_user}@{db_host}:{local_bind_port}\n")

    try:
        engine: Engine = create_engine(
            f"mysql+mysqldb://{db_user}:{db_password}@{db_host}:{local_bind_port}/{db_name}"
        )
        with engine.connect() as db_conn:
            sys.stdout.write("DB:  Connected.\n")
            yield db_conn
    finally:
        sys.stdout.write("DB:  Connection closed.\n")
