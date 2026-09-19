import re
import socket
import time
import uuid
from contextlib import contextmanager
from urllib.parse import urlparse

from gns3_client import gns3_request
from network_services import SERVER_URL, PROJECT_ID

SERVER_USERNAME = "ubuntu"
SERVER_PASSWORD = "ubuntu"


def get_nodes_by_name():
    nodes = gns3_request(
        SERVER_URL,
        "GET",
        f"/v2/projects/{PROJECT_ID}/nodes",
    )
    return {node["name"]: node for node in nodes}


def get_console_host(node):
    host = node.get("console_host")

    if host in (None, "", "0.0.0.0", "::"):
        return urlparse(SERVER_URL).hostname

    return host


def send_line(connection, text=""):
    connection.sendall((text + "\n").encode())


def read_until(connection, patterns, timeout=15):
    output = ""
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        try:
            data = connection.recv(4096)

            if not data:
                break

            output += data.decode("utf-8", errors="ignore")

            if any(pattern in output for pattern in patterns):
                return output

        except socket.timeout:
            continue

    raise TimeoutError(
        f"Beklenen ifade gelmedi: {patterns}\n{output}"
    )


def login(
    connection,
    username=SERVER_USERNAME,
    password=SERVER_PASSWORD,
):
    send_line(connection)

    output = read_until(
        connection,
        ["login:", "$ ", "# "],
        timeout=20,
    )

    if "$ " in output or "# " in output:
        return

    send_line(connection, username)
    read_until(connection, ["Password:"], timeout=15)

    send_line(connection, password)
    read_until(connection, ["$ ", "# "], timeout=20)


def run_command(connection, command, timeout=30):
    marker = f"CMD_DONE_{uuid.uuid4().hex}"

    send_line(
        connection,
        f'{command}; printf "\\n{marker}:%s\\n" "$?"',
    )

    output = ""
    deadline = time.monotonic() + timeout
    pattern = rf"\r?\n{re.escape(marker)}:(\d+)\r?\n"

    while time.monotonic() < deadline:
        try:
            data = connection.recv(4096)

            if not data:
                break

            output += data.decode("utf-8", errors="ignore")
            match = re.search(pattern, output)

            if match:
                command_output = output[:match.start()]
                lines = command_output.replace("\r", "").splitlines()

                # Console tarafindan geri yazilan komutu kaldir.
                if lines:
                    lines = lines[1:]

                return (
                    "\n".join(lines).strip(),
                    int(match.group(1)),
                )

        except socket.timeout:
            continue

    raise TimeoutError(f"Komut tamamlanmadi: {command}")


def run_checked(connection, command, timeout=30):
    output, exit_code = run_command(
        connection,
        command,
        timeout=timeout,
    )

    print(f"\n$ {command}")

    if output:
        print(output)

    print("Exit code:", exit_code)

    if exit_code != 0:
        raise RuntimeError(
            f"Komut basarisiz: {command}"
        )

    return output


@contextmanager
def open_server_console(
    server_name,
    username=SERVER_USERNAME,
    password=SERVER_PASSWORD,
):
    nodes_by_name = get_nodes_by_name()
    node = nodes_by_name.get(server_name)

    if not node:
        raise RuntimeError(
            f"GNS3 projesinde node bulunamadi: {server_name}"
        )

    if node.get("status") != "started":
        raise RuntimeError(
            f"Node calismiyor: {server_name}"
        )

    host = get_console_host(node)
    port = node.get("console")

    if port is None:
        raise RuntimeError(
            f"Console port bulunamadi: {server_name}"
        )

    print(f"\n=== {server_name}: {host}:{port} ===")

    connection = socket.create_connection(
        (host, int(port)),
        timeout=10,
    )
    connection.settimeout(1)

    try:
        login(
            connection,
            username=username,
            password=password,
        )
        yield connection
    finally:
        connection.close()