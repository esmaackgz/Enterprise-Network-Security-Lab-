from urllib.parse import urlparse

from gns3_client import gns3_request
from server_inventory import SERVERS

SERVER_URL = "http://100.98.251.22:80"
PROJECT_ID = "1c320728-4402-4ddf-930e-a99dc604e277"


def get_console_host(node):
    console_host = node.get("console_host")

    if not console_host or console_host in ("0.0.0.0", "::"):
        return urlparse(SERVER_URL).hostname

    return console_host


def main():
    nodes = gns3_request(
        SERVER_URL,
        "GET",
        f"/v2/projects/{PROJECT_ID}/nodes",
    )

    nodes_by_name = {
        node["name"]: node
        for node in nodes
    }

    print("\nSERVER INVENTORY - GNS3 NODE ESLESMESI")
    print("=" * 100)
    print(
        f"{'SERVER':<22} "
        f"{'IP':<15} "
        f"{'STATUS':<10} "
        f"{'CONSOLE_HOST':<18} "
        f"{'CONSOLE':<8} "
        f"{'CONSOLE_TYPE':<14} "
        f"{'NODE_ID'}"
    )
    print("-" * 100)

    missing = []

    for server in SERVERS:
        node = nodes_by_name.get(server["name"])

        if not node:
            missing.append(server["name"])
            print(
                f"{server['name']:<22} "
                f"{server['ip']:<15} "
                f"{'MISSING':<10} "
                f"{'-':<18} "
                f"{'-':<8} "
                f"{'-':<14} "
                f"-"
            )
            continue

        print(
            f"{server['name']:<22} "
            f"{server['ip']:<15} "
            f"{node.get('status', '-'):<10} "
            f"{get_console_host(node):<18} "
            f"{str(node.get('console', '-')):<8} "
            f"{str(node.get('console_type', '-')):<14} "
            f"{node.get('node_id', '-')}"
        )

    print("=" * 100)

    if missing:
        print("\nGNS3 projesinde bulunamayan server node'lari:")
        for name in missing:
            print("-", name)
    else:
        print("\nOK: server_inventory.py icindeki tum serverlar GNS3 projesinde bulundu.")


if __name__ == "__main__":
    main()