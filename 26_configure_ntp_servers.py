from server_console import open_server_console, run_checked
import shlex

NTP_SERVERS = [
    {
        "name": "NTP1",
        "hostname": "ntp1",
        "ip": "10.10.140.31",
        "peer": "10.10.140.32",
    },
    {
        "name": "NTP2",
        "hostname": "ntp2",
        "ip": "10.10.140.32",
        "peer": "10.10.140.31",
    },
]

AD_DNS_SERVERS = ("10.10.130.11", "10.10.130.12")
DNS_DOMAIN = "corp.local"

NTP_ALLOW_NETWORKS = [
    "10.10.0.0/16",
    "192.168.99.0/24",
]


def write_remote_file(connection, path, content):
    quoted_content = shlex.quote(content)
    quoted_path = shlex.quote(path)

    run_checked(
        connection,
        f"printf %s {quoted_content} | sudo -n tee {quoted_path} >/dev/null",
    )


def configure_hosts_file(connection, server):
    hosts_content = f"""127.0.0.1 localhost
{server["ip"]} {server["hostname"]}.corp.local {server["hostname"]}

::1 localhost ip6-localhost ip6-loopback
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters
"""
    write_remote_file(connection, "/etc/hosts", hosts_content)


def configure_resolver(connection):
    resolv_conf = f"""nameserver {AD_DNS_SERVERS[0]}
nameserver {AD_DNS_SERVERS[1]}
search {DNS_DOMAIN}
"""
    run_checked(connection, "sudo -n rm -f /etc/resolv.conf")
    write_remote_file(connection, "/etc/resolv.conf", resolv_conf)

    run_checked(connection, "timeout 15 getent ahostsv4 archive.ubuntu.com")


def install_chrony(connection):
    apt_options = (
        "-o Acquire::ForceIPv4=true "
        "-o Acquire::Retries=1 "
        "-o Acquire::http::Timeout=20 "
        "-o Acquire::https::Timeout=20 "
    )

    run_checked(
        connection,
        "sudo -n systemctl disable --now apt-daily.timer apt-daily-upgrade.timer || true",
        timeout=60,
    )
    run_checked(
        connection,
        "sudo -n systemctl stop apt-daily.service apt-daily-upgrade.service || true",
        timeout=60,
    )
    run_checked(connection, "sudo -n dpkg --configure -a", timeout=180)

    run_checked(
        connection,
        f"sudo -n apt-get {apt_options} update",
        timeout=900,
    )

    run_checked(
        connection,
        "sudo -n DEBIAN_FRONTEND=noninteractive "
        f"apt-get {apt_options} install -y chrony",
        timeout=900,
    )


def configure_chrony(connection, peer_ip):
    allow_lines = "\n".join(
        f"allow {network}"
        for network in NTP_ALLOW_NETWORKS
    )

    chrony_conf = f"""pool tr.pool.ntp.org iburst
pool pool.ntp.org iburst

server {peer_ip} iburst

local stratum 10
manual
rtcsync

bindaddress 0.0.0.0

{allow_lines}
"""

    write_remote_file(connection, "/etc/chrony/chrony.conf", chrony_conf)

    run_checked(connection, "sudo -n systemctl enable --now chrony", timeout=120)
    run_checked(connection, "sudo -n systemctl restart chrony", timeout=120)


def verify_ntp(connection):
    run_checked(connection, "sudo -n systemctl is-active chrony")
    run_checked(connection, "chronyc tracking", timeout=60)
    run_checked(connection, "chronyc sources -v", timeout=60)
    run_checked(connection, "sudo -n ss -lunp | grep ':123'")


def configure_ntp_server(server):
    with open_server_console(server["name"]) as connection:
        print(f"{server['name']} NTP/chrony kurulumu basliyor...")

        run_checked(connection, f"sudo -n hostnamectl set-hostname {server['hostname']}")
        configure_hosts_file(connection, server)
        configure_resolver(connection)
        install_chrony(connection)
        configure_chrony(connection, server["peer"])
        verify_ntp(connection)

        print(f"OK: {server['name']} NTP/chrony kurulumu tamamlandi.")


def main():
    for server in NTP_SERVERS:
        configure_ntp_server(server)

    print("OK: NTP1 ve NTP2 kurulumu tamamlandi.")


if __name__ == "__main__":
    main()