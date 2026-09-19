from server_console import open_server_console, run_checked


SERVERS = ["NTP1", "NTP2"]


def main():
    for server in SERVERS:
        with open_server_console(server) as connection:
            print(f"\n=== {server} NTP dogrulama ===")
            run_checked(connection, "hostname -f")
            run_checked(connection, "cat /etc/hosts")
            run_checked(connection, "cat /etc/resolv.conf")
            run_checked(connection, "sudo -n systemctl is-active chrony")
            run_checked(connection, "chronyc tracking", timeout=60)
            run_checked(connection, "chronyc sources -v", timeout=60)
            run_checked(connection, "sudo -n chronyc clients", timeout=60)
            run_checked(connection, "sudo -n ss -lunp | grep ':123'")


if __name__ == "__main__":
    main()