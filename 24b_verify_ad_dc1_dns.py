from server_console import open_server_console, run_checked


SERVER_NAME = "AD-DC1"


def main():
    with open_server_console(SERVER_NAME) as connection:
        run_checked(connection, "hostname -f")
        run_checked(connection, "cat /etc/resolv.conf")
        run_checked(connection, "sudo -n systemctl is-active samba-ad-dc")

        run_checked(connection, "host -t A corp.local 127.0.0.1")
        run_checked(connection, "host -t SRV _ldap._tcp.corp.local 127.0.0.1")
        run_checked(connection, "host -t SRV _kerberos._udp.corp.local 127.0.0.1")

        run_checked(connection, "timeout 15 host archive.ubuntu.com 127.0.0.1")
        run_checked(connection, "timeout 15 getent ahostsv4 archive.ubuntu.com")

        run_checked(connection, "sudo -n ss -lntup | grep ':53'")

        print("OK: AD-DC1 DNS, LDAP/Kerberos SRV ve dis DNS forward testi basarili.")


if __name__ == "__main__":
    main()