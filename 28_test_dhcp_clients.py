from server_console import open_server_console, run_checked


CLIENTS = [
    {
        "name": "USER-PC1",
        "expected_prefix": "10.10.10.",
        "gateway": "10.10.10.1",
        "dns": ["10.10.130.11", "10.10.130.12"],
    },
    {
        "name": "USER-PC2",
        "expected_prefix": "10.10.10.",
        "gateway": "10.10.10.1",
        "dns": ["10.10.130.11", "10.10.130.12"],
    },
    {
        "name": "USER-PC3",
        "expected_prefix": "10.10.10.",
        "gateway": "10.10.10.1",
        "dns": ["10.10.130.11", "10.10.130.12"],
    },
    {
        "name": "GUEST-PC1",
        "expected_prefix": "10.10.40.",
        "gateway": "10.10.40.1",
        "dns": ["10.10.130.21", "10.10.130.22"],
    },
    {
        "name": "GUEST-PC2",
        "expected_prefix": "10.10.40.",
        "gateway": "10.10.40.1",
        "dns": ["10.10.130.21", "10.10.130.22"],
    },
    {
        "name": "VOICE-PC1",
        "expected_prefix": "10.10.30.",
        "gateway": "10.10.30.1",
        "dns": ["10.10.130.11", "10.10.130.12"],
    },
    {
        "name": "VOICE-PC2",
        "expected_prefix": "10.10.30.",
        "gateway": "10.10.30.1",
        "dns": ["10.10.130.11", "10.10.130.12"],
    },
    {
        "name": "PRINTER1",
        "expected_prefix": "10.10.35.",
        "gateway": "10.10.35.1",
        "dns": ["10.10.130.11", "10.10.130.12"],
    },
    {
        "name": "CAMERA1",
        "expected_prefix": "10.10.36.",
        "gateway": "10.10.36.1",
        "dns": ["10.10.130.21", "10.10.130.22"],
    },
]



def verify_client(connection, client):
    ip_output = run_checked(
        connection,
        "ip -4 -o addr show dev eth0 | awk '{print $4}'",
    )

    route_output = run_checked(connection, "ip route")
    resolv_output = run_checked(connection, "cat /etc/resolv.conf || true")

    run_checked(connection, f"ping -c 2 -W 2 {client['gateway']}")
    run_checked(connection, "timeout 10 getent ahostsv4 archive.ubuntu.com || true")

    if client["expected_prefix"] not in ip_output:
        raise RuntimeError(
            f"{client['name']} beklenen VLAN IP almadi. "
            f"Beklenen prefix: {client['expected_prefix']} Cikti: {ip_output}"
        )

    if f"default via {client['gateway']}" not in route_output:
        raise RuntimeError(
            f"{client['name']} default gateway hatali. "
            f"Beklenen: {client['gateway']}"
        )

    missing_dns = [
        dns for dns in client["dns"]
        if dns not in resolv_output
    ]

    if missing_dns:
        print(
            f"UYARI: {client['name']} /etc/resolv.conf icinde beklenen DNS gorunmedi: "
            f"{', '.join(missing_dns)}"
        )

    print(f"OK: {client['name']} DHCP testi basarili.")


def test_client(client):
    with open_server_console(client["name"]) as connection:
        print(f"\n=== {client['name']} DHCP testi ===")
        verify_client(connection, client)

def main():
    for client in CLIENTS:
        test_client(client)

    print("OK: DHCP client testleri tamamlandi.")


if __name__ == "__main__":
    main()