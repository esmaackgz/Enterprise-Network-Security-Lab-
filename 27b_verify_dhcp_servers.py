from server_console import open_server_console, run_checked


SERVERS = ["DHCP1", "DHCP2"]


def main():
    for server in SERVERS:
        with open_server_console(server) as connection:
            print(f"\n=== {server} DHCP dogrulama ===")
            run_checked(connection, "hostname -f")
            run_checked(connection, "sudo -n systemctl is-active isc-dhcp-server")
            run_checked(connection, "sudo -n dhcpd -t -cf /etc/dhcp/dhcpd.conf")
            run_checked(connection, "sudo -n ss -lunp | grep ':67'")
            run_checked(connection, "grep -E 'range|subnet 10.10|domain-name-servers|ntp-servers' /etc/dhcp/dhcpd.conf")


if __name__ == "__main__":
    main()