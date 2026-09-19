import socket
import time
from urllib.parse import urlparse

from gns3_client import gns3_request

SERVER_URL = "http://100.98.251.22:80"
PROJECT_ID = "1c320728-4402-4ddf-930e-a99dc604e277"
TARGETS = {"NTP1", "NTP2"}


def console_host(node):
    host = node.get("console_host")

    if not host or host in ("0.0.0.0", "::"):
        return urlparse(SERVER_URL).hostname

    return host


def read_console(connection, duration=4):
    output = []
    end_time = time.monotonic() + duration

    while time.monotonic() < end_time:
        try:
            data = connection.recv(4096)

            if not data:
                break

            output.append(data)

        except socket.timeout:
            break

    return b"".join(output).decode("utf-8", errors="ignore")


def main():
    nodes = gns3_request(
        SERVER_URL,
        "GET",
        f"/v2/projects/{PROJECT_ID}/nodes",
    )

    nodes_by_name = {node["name"]: node for node in nodes}

    for name in sorted(TARGETS):
        node = nodes_by_name[name]
        host = console_host(node)
        port = node["console"]

        print(f"\n=== {name}: {host}:{port} ===")

        try:
            with socket.create_connection((host, port), timeout=10) as connection:
                connection.settimeout(2)
                connection.sendall(b"\r\n")
                time.sleep(1)

                output = read_console(connection)
                print(output or "[Console acildi fakat cikti gelmedi]")

        except Exception as error:
            print("[HATA]", error)


if __name__ == "__main__":
    main()