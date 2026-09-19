import shlex

from server_console import open_server_console, run_checked


DHCP_SERVERS = [
    {"name": "DHCP1", "hostname": "dhcp1", "ip": "10.10.130.31", "pool": "primary"},
    {"name": "DHCP2", "hostname": "dhcp2", "ip": "10.10.130.32", "pool": "secondary"},
]

AD_DNS = "10.10.130.11, 10.10.130.12"
PUBLIC_DNS = "10.10.130.21, 10.10.130.22"
NTP_SERVERS = "10.10.140.31, 10.10.140.32"

SCOPES = [
    {
        "name": "VLAN10_USER",
        "subnet": "10.10.10.0",
        "gateway": "10.10.10.1",
        "dns": AD_DNS,
        "domain": "corp.local",
        "primary_range": ("10.10.10.50", "10.10.10.149"),
        "secondary_range": ("10.10.10.150", "10.10.10.240"),
    },
    {
        "name": "VLAN30_VOICE",
        "subnet": "10.10.30.0",
        "gateway": "10.10.30.1",
        "dns": AD_DNS,
        "domain": "corp.local",
        "primary_range": ("10.10.30.50", "10.10.30.149"),
        "secondary_range": ("10.10.30.150", "10.10.30.240"),
    },
    {
        "name": "VLAN35_PRINTER",
        "subnet": "10.10.35.0",
        "gateway": "10.10.35.1",
        "dns": AD_DNS,
        "domain": "corp.local",
        "primary_range": ("10.10.35.50", "10.10.35.149"),
        "secondary_range": ("10.10.35.150", "10.10.35.240"),
    },
    {
        "name": "VLAN36_IOTCAMERA",
        "subnet": "10.10.36.0",
        "gateway": "10.10.36.1",
        "dns": PUBLIC_DNS,
        "domain": "",
        "primary_range": ("10.10.36.50", "10.10.36.149"),
        "secondary_range": ("10.10.36.150", "10.10.36.240"),
    },
    {
        "name": "VLAN40_GUEST",
        "subnet": "10.10.40.0",
        "gateway": "10.10.40.1",
        "dns": PUBLIC_DNS,
        "domain": "",
        "primary_range": ("10.10.40.50", "10.10.40.149"),
        "secondary_range": ("10.10.40.150", "10.10.40.240"),
    },
]


def write_remote_file(connection, path, content):
    run_checked(
        connection,
        f"printf %s {shlex.quote(content)} | sudo -n tee {shlex.quote(path)} >/dev/null",
    )


def configure_hosts_file(connection, server):
    content = f"""127.0.0.1 localhost
{server["ip"]} {server["hostname"]}.corp.local {server["hostname"]}

::1 localhost ip6-localhost ip6-loopback
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters
"""
    write_remote_file(connection, "/etc/hosts", content)


def configure_resolver(connection):
    content = """nameserver 10.10.130.11
nameserver 10.10.130.12
search corp.local
"""
    run_checked(connection, "sudo -n rm -f /etc/resolv.conf")
    write_remote_file(connection, "/etc/resolv.conf", content)
    run_checked(connection, "timeout 15 getent ahostsv4 archive.ubuntu.com")


def build_dhcpd_conf(pool_name):
    lines = [
        "default-lease-time 3600;",
        "max-lease-time 14400;",
        "authoritative;",
        "ddns-update-style none;",
        "",
        "subnet 10.10.130.0 netmask 255.255.255.0 {",
        "}",
        "",
    ]

    for scope in SCOPES:
        start_ip, end_ip = scope[f"{pool_name}_range"]
        broadcast = scope["subnet"].rsplit(".", 1)[0] + ".255"

        lines.extend([
            f"# {scope['name']}",
            f"subnet {scope['subnet']} netmask 255.255.255.0 {{",
            f"  range {start_ip} {end_ip};",
            f"  option routers {scope['gateway']};",
            f"  option broadcast-address {broadcast};",
            "  option subnet-mask 255.255.255.0;",
            f"  option domain-name-servers {scope['dns']};",
            f"  option ntp-servers {NTP_SERVERS};",
        ])

        if scope["domain"]:
            lines.append(f'  option domain-name "{scope["domain"]}";')

        lines.extend(["}", ""])

    return "\n".join(lines)


def install_dhcp_server(connection):
    apt_options = (
        "-o Acquire::ForceIPv4=true "
        "-o Acquire::Retries=1 "
        "-o Acquire::http::Timeout=20 "
        "-o Acquire::https::Timeout=20 "
    )

    run_checked(connection, "sudo -n dpkg --configure -a", timeout=180)
    run_checked(connection, f"sudo -n apt-get {apt_options} update", timeout=900)
    run_checked(
        connection,
        "sudo -n DEBIAN_FRONTEND=noninteractive "
        f"apt-get {apt_options} install -y isc-dhcp-server",
        timeout=900,
    )


def configure_service(connection, pool_name):
    write_remote_file(connection, "/etc/dhcp/dhcpd.conf", build_dhcpd_conf(pool_name))

    defaults = """INTERFACESv4="ens3"
INTERFACESv6=""
"""
    write_remote_file(connection, "/etc/default/isc-dhcp-server", defaults)

    run_checked(connection, "sudo -n dhcpd -t -cf /etc/dhcp/dhcpd.conf", timeout=60)
    run_checked(connection, "sudo -n systemctl enable --now isc-dhcp-server", timeout=120)
    run_checked(connection, "sudo -n systemctl restart isc-dhcp-server", timeout=120)


def verify(connection):
    run_checked(connection, "sudo -n systemctl is-active isc-dhcp-server")
    run_checked(connection, "sudo -n ss -lunp | grep ':67'")
    run_checked(connection, "sudo -n tail -n 20 /var/log/syslog | grep -i dhcp || true")


def configure_server(server):
    with open_server_console(server["name"]) as connection:
        print(f"{server['name']} DHCP kurulumu basliyor...")

        run_checked(connection, f"sudo -n hostnamectl set-hostname {server['hostname']}")
        configure_hosts_file(connection, server)
        configure_resolver(connection)
        install_dhcp_server(connection)
        configure_service(connection, server["pool"])
        verify(connection)

        print(f"OK: {server['name']} DHCP kurulumu tamamlandi.")


def main():
    for server in DHCP_SERVERS:
        configure_server(server)

    print("OK: DHCP1 ve DHCP2 scope kurulumu tamamlandi.")


if __name__ == "__main__":
    main()