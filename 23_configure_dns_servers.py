import base64
import shlex

from server_console import open_server_console, run_checked
from server_inventory import SERVERS

#Bu dosya DNS1/DNS2’ye BIND9 kuracak ve kurumsal recursive forwarder olarak ayarlayacak.

TARGETS = ("DNS1", "DNS2")
FORWARDERS = ("1.1.1.1", "9.9.9.9")

SERVERS_BY_NAME = {
    server["name"]: server
    for server in SERVERS
}


def write_remote_file(connection, path, content):
    encoded = base64.b64encode(
        content.encode("utf-8")
    ).decode("ascii")

    command = (
        f"printf %s {shlex.quote(encoded)} | "
        f"base64 -d | sudo -n tee {shlex.quote(path)} "
        f"> /dev/null"
    )

    run_checked(connection, command, timeout=60)


def create_bind_config(server_ip):
    return f"""acl trusted_clients {{
    127.0.0.0/8;
    10.10.0.0/16;
}};

options {{
    directory "/var/cache/bind";

    listen-on port 53 {{
        127.0.0.1;
        {server_ip};
    }};

    listen-on-v6 {{ none; }};

    recursion yes;
    allow-query {{ trusted_clients; }};
    allow-recursion {{ trusted_clients; }};
    allow-query-cache {{ trusted_clients; }};

    forwarders {{
        {FORWARDERS[0]};
        {FORWARDERS[1]};
    }};

    forward only;
    dnssec-validation auto;
    auth-nxdomain no;
    minimal-responses yes;
}};
"""


def configure_dns_server(server_name):
    server = SERVERS_BY_NAME[server_name]
    server_ip = server["ip"]

    with open_server_console(server_name) as connection:
        run_checked(
            connection,
            "timeout 15 resolvectl query archive.ubuntu.com",
            timeout=30,
        )

        run_checked(
            connection,
            "sudo -n apt-get update -qq -o Acquire::Retries=3",
            timeout=1800,
        )

        run_checked(
            connection,
            "sudo -n env DEBIAN_FRONTEND=noninteractive "
            "apt-get install -y bind9 bind9-utils dnsutils",
            timeout=900,
        )

        run_checked(
            connection,
            "sudo -n test -e "
            "/etc/bind/named.conf.options.pre-project "
            "|| sudo -n cp /etc/bind/named.conf.options "
            "/etc/bind/named.conf.options.pre-project",
        )

        write_remote_file(
            connection,
            "/etc/bind/named.conf.options",
            create_bind_config(server_ip),
        )

        run_checked(
            connection,
            "sudo -n named-checkconf /etc/bind/named.conf",
        )

        run_checked(
            connection,
            "sudo -n systemctl enable --now named",
            timeout=60,
        )

        run_checked(
            connection,
            "sudo -n systemctl restart named",
            timeout=60,
        )

        run_checked(
            connection,
            "systemctl is-active named",
        )

        run_checked(
            connection,
            "dig @127.0.0.1 archive.ubuntu.com A "
            "+time=10 +tries=2",
            timeout=30,
        )

        run_checked(
            connection,
            f"dig @{server_ip} archive.ubuntu.com A "
            "+time=10 +tries=2",
            timeout=30,
        )

        run_checked(
            connection,
            "sudo -n ss -lunpt | grep ':53 '",
        )

        print(
            f"OK: {server_name} BIND9 resolver kurulumu tamamlandi."
        )


def main():
    for server_name in TARGETS:
        try:
            configure_dns_server(server_name)
        except Exception as error:
            print(f"[HATA] {server_name}: {error}")


if __name__ == "__main__":
    main()