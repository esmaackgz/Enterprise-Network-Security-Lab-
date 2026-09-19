from server_console import open_server_console, run_checked


CLIENTS = [
    ("USER-PC1", "10.10.10.", "10.10.10.1"),
    ("GUEST-PC1", "10.10.40.", "10.10.40.1"),
    ("VOICE-PC1", "10.10.30.", "10.10.30.1"),
    ("PRINTER1", "10.10.35.", "10.10.35.1"),
    ("CAMERA1", "10.10.36.", "10.10.36.1"),
]


def main():
    for name, expected_prefix, gateway in CLIENTS:
        with open_server_console(name) as connection:
            print(f"\n=== {name} DHCP mevcut durum ===")

            ip_output = run_checked(
                connection,
                "ip -4 -o addr show dev eth0 | awk '{print $4}' || true",
            )
            route_output = run_checked(connection, "ip route || true")
            run_checked(connection, "cat /etc/resolv.conf || true")
            run_checked(connection, f"ping -c 2 -W 2 {gateway}")

            if expected_prefix not in ip_output:
                raise RuntimeError(
                    f"{name} beklenen VLAN IP almamis. "
                    f"Beklenen prefix: {expected_prefix}, IP cikti: {ip_output}"
                )

            if f"default via {gateway}" not in route_output:
                print(f"UYARI: {name} default gateway beklenen gibi gorunmedi: {gateway}")

            print(f"OK: {name} DHCP IP ve gateway testi basarili.")

    print("OK: DHCP client mevcut durum dogrulamasi tamamlandi.")


if __name__ == "__main__":
    main()