import contextlib
import sys
from collections.abc import Generator
from pathlib import Path
from typing import Any

from dotenv import dotenv_values
from sshtunnel import SSHTunnelForwarder


@contextlib.contextmanager
def get_ssh_connection(ssh_config_path: Path) -> Generator[int, Any, None]:
    """Open ssh tunnel using sshtunnel forwarder."""

    ssh_config_path = Path(ssh_config_path).expanduser()
    if not ssh_config_path.exists():
        raise FileNotFoundError(f"SSH config file not found at {ssh_config_path}.")

    config = dotenv_values(ssh_config_path)

    ssh_server = config["SSH_SERVER_IP"]
    ssh_user = config["SSH_USER"]
    ssh_key_path = Path(config["SSH_KEY_PATH"]).expanduser()
    remote_host = config["REMOTE_HOST"]
    local_bind_port = int(config["LOCAL_BIND_PORT"])
    remote_db_port = int(config["REMOTE_DB_PORT"])
    ssh_key_pass = config.get("SSH_KEY_PASS", None)

    # for var, val in config.items():
    #     if var not in ["SSH_KEY_PASS"]:
    #         sys.stdout.write(f"{var}: {val}\n")
    sys.stdout.write(
        f"SSH: Creating tunnel {ssh_server}->{local_bind_port}:"
        f"{remote_host}:{remote_db_port}\n"
    )
    server = SSHTunnelForwarder(
        (ssh_server, 22),
        ssh_username=ssh_user,
        ssh_pkey=str(ssh_key_path),
        ssh_private_key_password=ssh_key_pass,
        remote_bind_address=(remote_host, remote_db_port),
        local_bind_address=("127.0.0.1", local_bind_port),
        set_keepalive=10,
    )

    try:
        server.start()
        sys.stdout.write("SSH: Tunnel established.\n")
        # sys.stdout.write(f"Local port bound: {server.local_bind_port}.\n")
        yield server.local_bind_port
    finally:
        if server.is_active:
            server.stop()
            sys.stdout.write("SSH: Tunnel closed.\n")
