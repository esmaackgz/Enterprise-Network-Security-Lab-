import socket
import time
from urllib.parse import urlparse
import re
import uuid

from gns3_client import gns3_request
from network_services import SERVER_URL, PROJECT_ID


TARGETS = {"DNS1", "DNS2"}
#TARGETS = {"NTP1", "NTP2"}

USERNAME = "ubuntu"
PASSWORD = "ubuntu"


def get_console_host(node):
    host = node.get("console_host")
    return host if host not in (None, "", "0.0.0.0", "::") else urlparse(SERVER_URL).hostname


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

    raise TimeoutError(f"Beklenen ifade gelmedi: {patterns}\n{output}")


def send_line(connection, text=""):
    connection.sendall((text + "\n").encode())


def login(connection):
    send_line(connection)

    output = read_until(connection, ["login:", "$ ", "# "])

    if "$ " in output or "# " in output:
        return

    send_line(connection, USERNAME)
    read_until(connection, ["Password:"])
    send_line(connection, PASSWORD)
    read_until(connection, ["$ ", "# "])


def run_command(connection, command, timeout=30):
    marker = f"CMD_DONE_{uuid.uuid4().hex}"
    send_line(
        connection,
        f'{command}; printf "\\n{marker}:%s\\n" "$?"'
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

                # Terminalin geri yazdığı komut satırını çıkar.
                if lines:
                    lines = lines[1:]

                return "\n".join(lines).strip(), int(match.group(1))

        except socket.timeout:
            continue

    raise TimeoutError(f"Komut tamamlanmadi: {command}")

def main():
    nodes = gns3_request(
        SERVER_URL,
        "GET",
        f"/v2/projects/{PROJECT_ID}/nodes",
    )

    nodes_by_name = {node["name"]: node for node in nodes}

    for name in sorted(TARGETS):
        node = nodes_by_name[name]
        host = get_console_host(node)
        port = node["console"]

        print(f"\n=== {name}: {host}:{port} ===")

        try:
            with socket.create_connection(
                (host, port),
                timeout=10,
            ) as connection:
                connection.settimeout(1)
                login(connection)

                commands = [
                    "sudo -n resolvectl dns ens3 1.1.1.1 9.9.9.9",
                    "sudo -n resolvectl domain ens3 '~.'",
                    "sudo -n resolvectl flush-caches",
                    "sudo -n resolvectl reset-server-features",
                    "resolvectl status ens3",
                    "timeout 15 resolvectl query archive.ubuntu.com",
                    "timeout 15 bash -c '</dev/null >/dev/tcp/archive.ubuntu.com/443'",
                ]


                for command in commands:
                    output, exit_code = run_command(
                        connection,
                        command,
                    )

                    print(f"\n$ {command}")
                    print(output)
                    print("Exit code:", exit_code)

                    if exit_code != 0:
                        raise RuntimeError(
                            f"Komut basarisiz: {command}"
                        )

                print(
                    "OK: Console login, IP, route ve "
                    "gateway erisimi basarili."
                )

        except Exception as error:
            print(f"[HATA] {name}: {error}")


if __name__ == "__main__":
    main()