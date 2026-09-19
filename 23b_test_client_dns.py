from server_console import open_server_console, run_checked


CLIENTS = [
    {
        "name": "USER-PC1",
        "expected_dns": ["10.10.130.11", "10.10.130.12"],
        "internal_test": True,
    },
    {
        "name": "USER-PC2",
        "expected_dns": ["10.10.130.11", "10.10.130.12"],
        "internal_test": True,
    },
    {
        "name": "USER-PC3",
        "expected_dns": ["10.10.130.11", "10.10.130.12"],
        "internal_test": True,
    },
    {
        "name": "VOICE-PC1",
        "expected_dns": ["10.10.130.11", "10.10.130.12"],
        "internal_test": True,
    },
    {
        "name": "VOICE-PC2",
        "expected_dns": ["10.10.130.11", "10.10.130.12"],
        "internal_test": True,
    },
    {
        "name": "PRINTER1",
        "expected_dns": ["10.10.130.11", "10.10.130.12"],
        "internal_test": True,
    },
    {
        "name": "GUEST-PC1",
        "expected_dns": ["10.10.130.21", "10.10.130.22"],
        "internal_test": False,
    },
    {
        "name": "GUEST-PC2",
        "expected_dns": ["10.10.130.21", "10.10.130.22"],
        "internal_test": False,
    },
    {
        "name": "CAMERA1",
        "expected_dns": ["10.10.130.21", "10.10.130.22"],
        "internal_test": False,
    },
]


def check_dns_config(connection, client):
    resolv_output = run_checked(connection, "cat /etc/resolv.conf || true")

    for dns in client["expected_dns"]:
        if dns not in resolv_output:
            raise RuntimeError(
                f"{client['name']} beklenen DNS'i almamis: {dns}"
            )


def test_dns_resolution(connection, client):
    run_checked(connection, "timeout 10 getent ahostsv4 archive.ubuntu.com")

    if client["internal_test"]:
        run_checked(connection, "timeout 10 getent ahostsv4 ad-dc1.corp.local")
        run_checked(connection, "timeout 10 getent ahostsv4 ad-dc2.corp.local")
    else:
        output, _ = connection, None
        run_checked(connection, "timeout 10 getent ahostsv4 archive.ubuntu.com")


def main():
    for client in CLIENTS:
        with open_server_console(client["name"]) as connection:
            print(f"\n=== {client['name']} DNS testi ===")
            check_dns_config(connection, client)
            test_dns_resolution(connection, client)
            print(f"OK: {client['name']} DNS testi basarili.")

    print("OK: Client DNS testleri tamamlandi.")


if __name__ == "__main__":
    main()