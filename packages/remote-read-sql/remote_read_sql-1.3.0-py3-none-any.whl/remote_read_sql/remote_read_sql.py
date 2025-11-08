import sys
from pathlib import Path

import pandas as pd
from sqlalchemy.exc import OperationalError

from .remote_connect import remote_connect
from .safe_sql import safe_sql


def remote_read_sql(
    sql_query: str | None = None,
    *,
    ssh_config_path: Path,
    my_cnf_path: Path,
    my_cnf_connection_name: str,
    db_name: str,
) -> pd.DataFrame | None:
    """Read sql query into dataframe via ssh tunnel and mysql connection."""
    if sql_query:
        sql_query = safe_sql(sql_query)
        with remote_connect(
            ssh_config_path=ssh_config_path,
            my_cnf_path=my_cnf_path,
            my_cnf_connection_name=my_cnf_connection_name,
            db_name=db_name,
        ) as db_conn:
            try:
                df = pd.read_sql(sql_query, con=db_conn)
            except OperationalError as e:
                sys.stdout.write(f"Error executing query: {e}\n")
            else:
                return df
    return None
